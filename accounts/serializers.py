from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True},
            'role': {'required': True}
        }

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value.lower()

    def validate_role(self, value):
        """Validate role is one of the allowed choices"""
        if value not in ['candidate', 'recruiter', 'admin']:
            raise serializers.ValidationError("Invalid role. Choose from: candidate, recruiter, admin")
        return value

    def validate(self, attrs):
        """Additional validation"""
        # Recruiter domain validation
        if attrs.get('role') == 'recruiter':
            email = attrs.get('email', '')
            personal_domains = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
            ]
            domain = email.split('@')[-1].lower()
            if domain in personal_domains:
                raise serializers.ValidationError({
                    'email': 'Recruiters must use a company email address.'
                })
        
        return attrs

    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'full_name',
            'role',
            'is_verified',
            'is_active',
            'date_joined'
        )
        read_only_fields = ('id', 'date_joined')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ('full_name', 'email')
        extra_kwargs = {
            'email': {'read_only': True}  # Email cannot be changed
        }


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return attrs

    def validate_old_password(self, value):
        """Validate old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value