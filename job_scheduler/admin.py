from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

# from .models import Worker, Job
from .models import Worker, Job, Location


# dependency: pip install django-json-widget

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    # list_display = ("name", "address", "show_map", "map_thumbnail")
    list_display = ("name", "address", "map_thumbnail")

    @staticmethod
    def show_map(obj):
        coord = f"{obj.lat},{obj.long}"
        url = f'https://www.google.com/maps/search/?api=1&query={coord}'
        return format_html("<a href='{}' target='_blank'>Map Location</a>", url)

    @staticmethod
    def map_thumbnail(obj):
        from django.utils.html import format_html
        coord = f"{obj.lat},{obj.long}"
        apikey = 'AIzaSyCY9n8R9K5NdhNLjUJzZm_uaGXdpIYKQOY'
        url = f'https://www.google.com/maps/embed/v1/place?key={apikey}&q={coord}&zoom=16'
        # allowfullscreen is removed due to limited space
        return format_html("<iframe width='300' height='250' frameborder='0' style='border:0' src='{}'></iframe>", url)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "meeting_date", "view_location_link", "view_worker_link", "map_thumbnail")

    def view_location_link(self, obj):
        url = (
            reverse("admin:job_scheduler_location_change", args=({obj.location_id}))
        )
        return format_html('<a href="{}">{}</a>', url, obj.location)
        # return format_html('<a href="{}">{}</a>', url, f'{ obj.location.lat }, { obj.location.long }')

    view_location_link.short_description = "Location"

    def view_worker_link(self, obj):
        url = (
            reverse("admin:job_scheduler_worker_change", args=({obj.worker_id}))
        )
        return format_html('<a href="{}">{}</a>', url, obj.worker)

    view_worker_link.short_description = "Worker"

    @staticmethod
    def map_thumbnail(obj):
        from django.utils.html import format_html
        coord = f"{obj.location.lat},{obj.location.long}"
        apikey = 'AIzaSyCY9n8R9K5NdhNLjUJzZm_uaGXdpIYKQOY'
        url = f'https://www.google.com/maps/embed/v1/place?key={apikey}&q={coord}&zoom=16'
        # allowfullscreen is removed due to limited space
        return format_html("<iframe width='300' height='250' frameborder='0' style='border:0' src='{}'></iframe>", url)