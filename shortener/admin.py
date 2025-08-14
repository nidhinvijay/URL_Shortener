from django.contrib import admin
from .models import URL

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('original_url', 'short_code', 'clicks', 'created_at')
    search_fields = ('original_url', 'short_code')
