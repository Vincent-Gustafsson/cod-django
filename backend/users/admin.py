from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('slug',)
    readonly_fields = ('slug',)


admin.site.register(User, UserAdmin)
