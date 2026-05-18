from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import *

admin.site.register(Session)


@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    list_display = ['name','description']
    list_filter = ['name']
    search_fields = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ['user','user_role','status']
    list_filter = ['user']
    search_fields = ['user']



@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):

    list_display = (
        "visitor_id",
        "user",
        "ip_address",
        "country",
        "city",
        "pageviews_count",
        "clicks_count",
        "searches_count",
        "first_seen",
        "last_seen",
    )

    list_filter = (
        "country",
        "city",
        "first_seen",
    )

    search_fields = (
        "visitor_id",
        "ip_address",
        "country",
        "city",
    )

    readonly_fields = (
        "visitor_id",
        "first_seen",
        "last_seen",
        "analytics_summary",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(
            pv_count=Count("pageview", distinct=True),
            click_count=Count("clickevent", distinct=True),
            search_count=Count("searchevent", distinct=True),
        )

    def pageviews_count(self, obj):
        return obj.pv_count
    pageviews_count.admin_order_field = "pv_count"

    def clicks_count(self, obj):
        return obj.click_count
    clicks_count.admin_order_field = "click_count"

    def searches_count(self, obj):
        return obj.search_count
    searches_count.admin_order_field = "search_count"

    def analytics_summary(self, obj):
        return format_html(
            """
            <div style="padding:10px;">
                <h3>Analytics Summary</h3>
                <ul>
                    <li><b>Visitor ID:</b> {}</li>
                    <li><b>Country:</b> {}</li>
                    <li><b>City:</b> {}</li>
                    <li><b>IP:</b> {}</li>
                    <li><b>First Seen:</b> {}</li>
                    <li><b>Last Seen:</b> {}</li>
                </ul>
            </div>
            """,
            obj.visitor_id,
            obj.country,
            obj.city,
            obj.ip_address,
            obj.first_seen,
            obj.last_seen,
        )


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):

    list_display = (
        "path",
        "visitor",
        "session",
        "method",
        "timestamp",
    )

    list_filter = (
        "method",
        "timestamp",
        "path",
    )

    search_fields = (
        "path",
        "visitor__visitor_id",
        "session__session_key",
    )
    readonly_fields = (
        'visitor_id',
        'timestamp',
    )

    ordering = ("-timestamp",)


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):

    list_display = (
        "page",
        "label",
        "x",
        "y",
        "screen_width",
        "screen_height",
        "timestamp",
    )

    list_filter = (
        "page",
        "timestamp",
    )

    search_fields = (
        "label",
        "page",
    )
    readonly_fields = (
        "visitor_id",
        "timestamp",
    )
    ordering = ("-timestamp",)


@admin.register(SearchEvent)
class SearchEventAdmin(admin.ModelAdmin):

    list_display = (
        "query",
        "page",
        "visitor",
        "timestamp",
    )

    list_filter = (
        "timestamp",
    )

    search_fields = (
        "query",
    )

    ordering = ("-timestamp",)


@admin.register(FunnelEvent)
class FunnelEventAdmin(admin.ModelAdmin):

    list_display = (
        "funnel_name",
        "step_number",
        "step_name",
        "visitor",
        "session",
        "timestamp",
    )

    list_filter = (
        "funnel_name",
        "step_number",
        "timestamp",
    )

    search_fields = (
        "funnel_name",
        "step_name",
        "visitor__visitor_id",
    )

    ordering = ("funnel_name", "step_number")