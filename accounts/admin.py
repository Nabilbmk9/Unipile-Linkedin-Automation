from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, LinkedAccount
from .forms import CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ["email", "username", "is_staff", "is_active"]
    search_fields = ["email", "username"]
    ordering = ["email"]
    
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "username", "password1", "password2", "is_staff",
                "is_active", "is_superuser", "groups", "user_permissions"
            )}
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(LinkedAccount)
