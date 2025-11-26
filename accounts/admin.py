from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = ('email', 'full_name', 'role', 'is_verified', 'is_active', 'date_joined', 'status_badge')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'full_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'full_name', 'password')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
        ('Groups & Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_verified', 'is_active')
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def status_badge(self, obj):
        """Display colored status badge"""
        if obj.is_active and obj.is_verified:
            color = 'green'
            text = 'Active & Verified'
        elif obj.is_active:
            color = 'orange'
            text = 'Active (Not Verified)'
        else:
            color = 'red'
            text = 'Inactive'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related()
    
    actions = ['mark_as_verified', 'mark_as_unverified', 'activate_users', 'deactivate_users']
    
    def mark_as_verified(self, request, queryset):
        """Mark selected users as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} user(s) marked as verified.')
    mark_as_verified.short_description = "Mark selected users as verified"
    
    def mark_as_unverified(self, request, queryset):
        """Mark selected users as unverified"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} user(s) marked as unverified.')
    mark_as_unverified.short_description = "Mark selected users as unverified"
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = "Deactivate selected users"


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin for OTP model"""
    
    list_display = ('email', 'code', 'created_at', 'is_used', 'is_expired', 'status_badge')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def is_expired(self, obj):
        """Check if OTP is expired"""
        from django.utils import timezone
        return (timezone.now() - obj.created_at).total_seconds() > 600
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def status_badge(self, obj):
        """Display colored status badge"""
        from django.utils import timezone
        
        if obj.is_used:
            color = 'gray'
            text = 'Used'
        elif (timezone.now() - obj.created_at).total_seconds() > 600:
            color = 'red'
            text = 'Expired'
        else:
            color = 'green'
            text = 'Valid'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Disable manual OTP creation"""
        return False
    
    actions = ['delete_expired_otps']
    
    def delete_expired_otps(self, request, queryset):
        """Delete expired OTPs"""
        from django.utils import timezone
        count = 0
        for otp in queryset:
            if (timezone.now() - otp.created_at).total_seconds() > 600:
                otp.delete()
                count += 1
        self.message_user(request, f'{count} expired OTP(s) deleted.')
    delete_expired_otps.short_description = "Delete expired OTPs"