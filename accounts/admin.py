from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LinkedAccount
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "is_staff", "is_active"]
    search_fields = ["username", "email"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(LinkedAccount)
