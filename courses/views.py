from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Course, Module, Lesson, Assignment, AssignmentQuestion, Enrollment, LessonProgress, AssignmentSubmission
from .serializers import CourseListSerializer, CourseDetailSerializer, ModuleSerializer, LessonSerializer, AssignmentSerializer, EnrollmentSerializer, LessonProgressSerializer, AssignmentSubmissionSerializer
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated


# Public: list courses
class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer


# Public: course detail by slug + id
class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    lookup_field = "id"

    def get_object(self):
        # ensure slug matches too
        course_id = self.kwargs.get("id")
        slug = self.kwargs.get("slug")
        obj = get_object_or_404(Course, id=course_id, slug=slug)
        return obj


# Public: learn payload (modules + lessons + assignment) - check enrollment on frontend if necessary
@api_view(["GET"])
def course_learn_view(request, id, slug):
    course = get_object_or_404(Course, id=id, slug=slug)
    data = CourseDetailSerializer(course).data

    user = request.user
    enrolled = False
    lesson_progress = {}
    assignment_submissions = {}

    if user.is_authenticated:
        # check enrollment
        enrolled = Enrollment.objects.filter(user=user, course=course).exists()

        # get lesson completion map
        progress = LessonProgress.objects.filter(
            user=user, lesson__module__course=course
        )
        lesson_progress = {p.lesson_id: p.completed for p in progress}

        # get assignment submission map
        submissions = AssignmentSubmission.objects.filter(
            user=user, assignment__module__course=course
        )
        assignment_submissions = {
            s.assignment_id: {
                "submitted": True,
                "score": s.score,
                "answers": s.answers,
            }
            for s in submissions
        }

    data["enrolled"] = enrolled
    data["lesson_progress"] = lesson_progress
    data["assignment_status"] = assignment_submissions

    return Response(data)



# POST enroll
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def enroll_course_view(request, id):
    course = get_object_or_404(Course, id=id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    serializer = EnrollmentSerializer(enrollment)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# POST mark lesson complete
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def lesson_complete_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment_exists = Enrollment.objects.filter(user=request.user, course=lesson.module.course).exists()
    if not enrollment_exists:
        return Response({"detail": "Enroll to mark progress."}, status=status.HTTP_403_FORBIDDEN)

    lp, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    lp.completed = True
    lp.completed_at = timezone.now()
    lp.save()
    return Response({"detail": "Lesson marked complete."})


# POST submit assignment (MCQ)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@transaction.atomic
def assignment_submit_view(request, assignment_id):
    """
    Expect payload:
    {
      "answers": { "<question_id>": "<chosen_option>", ... }
    }
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.module.course
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        return Response({"detail": "Enroll to submit assignment."}, status=status.HTTP_403_FORBIDDEN)

    answers = request.data.get("answers", {})
    questions = list(assignment.questions.all())
    total = len(questions)
    correct = 0
    for q in questions:
        chosen = answers.get(str(q.id)) or answers.get(q.id)  # accept string keys
        if chosen is not None and str(chosen) == str(q.correct_answer):
            correct += 1

    score = (correct / total) * 100 if total else 0.0

    sub, created = AssignmentSubmission.objects.update_or_create(
        user=request.user,
        assignment=assignment,
        defaults={"answers": answers, "score": score}
    )

    resp = {
        "assignment_id": assignment.id,
        "total": total,
        "correct": correct,
        "score": score
    }
    return Response(resp, status=status.HTTP_200_OK)

# GET enrolled courses for dashboard
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_courses_view(request):
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related("course")

    data = []
    for e in enrollments:
        course = e.course
        completed_lessons = LessonProgress.objects.filter(
            user=user, lesson__module__course=course, completed=True
        ).count()

        total_lessons = Lesson.objects.filter(
            module__course=course
        ).count()

        progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        data.append({
            "id": course.id,
            "title": course.title,
            "thumbnail": course.thumbnail,
            "slug": course.slug,
            "progress": progress,
            "status": "Completed" if progress == 100 else "Ongoing",
        })

    return Response(data)


