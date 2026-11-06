from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile details"
    fields = ("bio", "agreement_accepted", "avatar")


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    list_display = (
        "pk",
        "username",
        "email",
        "bio",
        "is_staff",
        "is_active",
    )
    list_display_links = ("pk", "username")
    search_fields = ("username", "email", "first_name", "last_name")

    fieldsets = [
        (
            None,
            {
                "fields": ("username", "password"),
            },
        ),
        (
            "Personal options",
            {
                "fields": ("first_name", "last_name", "email"),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
    ]

    @admin.display(description="Био")
    def bio(self, obj: User) -> str:
        profile = getattr(obj, "profile", None)
        return profile.bio if profile else "Нет био"
