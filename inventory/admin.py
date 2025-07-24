from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InventoryItem, RequestItem, Notification
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'location']
    search_fields = ['name', 'location']
    list_filter = ['category']

@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    list_display = ['requester', 'item', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['item__name', 'requester__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['user__username', 'message']
