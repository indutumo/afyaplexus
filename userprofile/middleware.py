from urllib.parse import urlparse

from django.utils import timezone
from user_agents import parse

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

        # -----------------------------
        # IGNORE INVALID PAGES
        # -----------------------------
        if response.status_code == 404:
            return response

        if not request.resolver_match:
            return response

        ignored_paths = [
            "/static/",
            "/media/",
            "/admin/",
            "userprofile",
            "/favicon.ico",
            "/.well-known",
        ]

        for path in ignored_paths:
            if request.path.startswith(path):
                return response

        try:

            # -----------------------------
            # VISITOR ID
            # -----------------------------
            visitor_id = request.COOKIES.get(
                "visitor_id"
            )

            if not visitor_id:
                visitor_id = generate_visitor_id()

            # -----------------------------
            # SESSION
            # -----------------------------
            if not request.session.session_key:
                request.session.save()

            # -----------------------------
            # REQUEST INFO
            # -----------------------------
            ip = get_client_ip(request)

            geo = get_geo_data(ip)

            user_agent_string = request.META.get(
                "HTTP_USER_AGENT",
                ""
            )

            ua = parse(user_agent_string)

            referrer = request.META.get(
                "HTTP_REFERER"
            )

            # -----------------------------
            # VISITOR
            # -----------------------------
            visitor, created = Visitor.objects.get_or_create(
                visitor_id=visitor_id
            )

            # Visit count
            if not created:
                visitor.visit_count += 1

            # User
            if request.user.is_authenticated:
                visitor.user = request.user

            # Activity
            visitor.last_activity = timezone.now()

            # Network
            visitor.ip_address = ip

            # Location
            visitor.country = geo.get("country")
            visitor.region = geo.get("region")
            visitor.city = geo.get("city")
            visitor.timezone = geo.get("timezone")
            visitor.latitude = geo.get("lat")
            visitor.longitude = geo.get("lon")

            # Device
            visitor.user_agent = user_agent_string
            visitor.browser = ua.browser.family
            visitor.browser_version = ua.browser.version_string
            visitor.operating_system = ua.os.family
            visitor.device_type = (
                "Mobile" if ua.is_mobile else
                "Tablet" if ua.is_tablet else
                "Desktop"
            )

            visitor.is_mobile = ua.is_mobile
            visitor.is_tablet = ua.is_tablet
            visitor.is_desktop = ua.is_pc

            visitor.device_brand = ua.device.brand

            # Traffic source
            visitor.referrer = referrer

            if referrer:
                visitor.referrer_domain = (
                    urlparse(referrer).netloc
                )

            # Landing page
            if not visitor.landing_page:
                visitor.landing_page = request.path

            # UTM
            visitor.utm_source = request.GET.get(
                "utm_source"
            )

            visitor.utm_medium = request.GET.get(
                "utm_medium"
            )

            visitor.utm_campaign = request.GET.get(
                "utm_campaign"
            )

            # Basic bot detection
            bot_keywords = [
                "bot",
                "crawl",
                "spider",
                "slurp"
            ]

            ua_lower = user_agent_string.lower()

            visitor.is_bot = any(
                word in ua_lower
                for word in bot_keywords
            )

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
            PageView.objects.create(
                visitor=visitor,
                session=session_obj,
                path=request.path,
                full_url=request.build_absolute_uri(),
                view_name=request.resolver_match.view_name,
                method=request.method,
                referrer=referrer
            )

            # Increase page views
            visitor.total_page_views += 1
            visitor.save(update_fields=[
                "total_page_views"
            ])

            # -----------------------------
            # COOKIE
            # -----------------------------
            response.set_cookie(
                "visitor_id",
                visitor_id,
                max_age=60 * 60 * 24 * 365
            )

            request.analytics_visitor = visitor
            request.analytics_session = session_obj

        except Exception:
            pass

        return response