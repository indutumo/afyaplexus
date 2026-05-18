from .models import Visitor, Session, PageView
from .utils import (
    generate_visitor_id,
    get_client_ip,
    get_geo_data
)


class AnalyticsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        ignored_paths = [
            "/static/",
            "/media/",
            "/admin/",
            "/favicon.ico",
            "/.well-known",
            "/userprofile/",
        ]

        for path in ignored_paths:
            if request.path.startswith(path):
                return response

        visitor_id = request.COOKIES.get("visitor_id")

        if not visitor_id:
            visitor_id = generate_visitor_id()

        if not request.session.session_key:
            request.session.save()

        ip = get_client_ip(request)

        # 🌍 GEO DATA
        geo = get_geo_data(ip)

        # -----------------------------
        # VISITOR (SAFE UPSERT LOGIC)
        # -----------------------------
        visitor, created = Visitor.objects.get_or_create(
            visitor_id=visitor_id
        )

        # ALWAYS UPDATE (fix missing lat/lon issue)
        visitor.ip_address = ip
        visitor.user_agent = request.META.get("HTTP_USER_AGENT", "")

        if request.user.is_authenticated:
            visitor.user = request.user

        visitor.country = geo.get("country")
        visitor.city = geo.get("city")
        visitor.latitude = geo.get("lat")
        visitor.longitude = geo.get("lon")

        visitor.save()

        # -----------------------------
        # SESSION
        # -----------------------------
        session_obj, _ = Session.objects.get_or_create(
            session_key=request.session.session_key,
            defaults={"visitor": visitor}
        )

        # -----------------------------
        # PAGE VIEW
        # -----------------------------
        view_name = None

        if request.resolver_match:
            view_name = request.resolver_match.view_name

        PageView.objects.create(
            visitor=visitor,
            session=session_obj,
            path=request.path,
            full_url=request.build_absolute_uri(),
            view_name=view_name,
            method=request.method,
            referrer=request.META.get("HTTP_REFERER")
        )

        # -----------------------------
        # COOKIE RESPONSE
        # -----------------------------
        response.set_cookie(
            "visitor_id",
            visitor_id,
            max_age=60 * 60 * 24 * 365
        )

        request.analytics_visitor = visitor
        request.analytics_session = session_obj

        return response