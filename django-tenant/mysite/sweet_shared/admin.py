from django.contrib import admin

from sweet_shared.models import SweetType

@admin.register(SweetType)
class SweetAdmin(admin.ModelAdmin):
    list_display = ('name',)