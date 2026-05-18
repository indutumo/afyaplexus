from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.views.generic import ListView, UpdateView, CreateView,DeleteView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
import uuid, json, requests
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string, get_template 
from django.template import Context, Template, RequestContext
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.utils.timezone import now

def is_valid_queryparam(param):
    return param != '' and param is not None


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            auth_login(request, user)
            return JsonResponse({
                "success": True,
                "redirect": request.POST.get("next") or "/"
            })

        return JsonResponse({
            "success": False,
            "error": "Invalid credentials"
        })

def logout_view(request):
    logout(request)
    return redirect('/')

def profile(request):
    return render(request, 'account/profile.html')


# analytics/views.py

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import (
    ClickEvent,
    SearchEvent,
    PageView
)

from django.db.models import Count
from django.db.models.functions import TruncDate


import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import (
    ClickEvent,
    SearchEvent
)


@csrf_exempt
def track_click(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body or "{}")

        # -------------------------
        # ALWAYS RESOLVE SESSION HERE
        # -------------------------
        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key

        visitor_id = request.COOKIES.get("visitor_id")

        if not visitor_id:
            visitor_id = str(uuid.uuid4())

        visitor, _ = Visitor.objects.get_or_create(
            visitor_id=visitor_id
        )

        session_obj, _ = Session.objects.get_or_create(
            session_key=session_key,
            defaults={"visitor": visitor}
        )

        ClickEvent.objects.create(
            visitor=visitor,
            session=session_obj,
            page=data.get("page", ""),
            event_type=data.get("event_type", "click"),
            label=data.get("label", ""),
            x=data.get("x"),
            y=data.get("y"),
            screen_width=data.get("screen_width"),
            screen_height=data.get("screen_height"),
        )

        response = JsonResponse({"status": "ok"})
        response.set_cookie("visitor_id", visitor_id, max_age=60 * 60 * 24 * 365)

        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@csrf_exempt
def track_search(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body or "{}")

        # -------------------------
        # ENSURE SESSION EXISTS
        # -------------------------
        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key

        # -------------------------
        # VISITOR COOKIE
        # -------------------------
        visitor_id = request.COOKIES.get("visitor_id")

        if not visitor_id:
            visitor_id = str(uuid.uuid4())

        visitor, _ = Visitor.objects.get_or_create(
            visitor_id=visitor_id
        )

        session_obj, _ = Session.objects.get_or_create(
            session_key=session_key,
            defaults={"visitor": visitor}
        )

        # -------------------------
        # CREATE SEARCH EVENT
        # -------------------------
        SearchEvent.objects.create(
            visitor=visitor,
            session=session_obj,
            query=data.get("query", ""),
            page=data.get("page", "")
        )

        response = JsonResponse({"status": "ok"})
        response.set_cookie(
            "visitor_id",
            visitor_id,
            max_age=60 * 60 * 24 * 365
        )

        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def analytics_summary(request):

    total_pageviews = PageView.objects.count()

    unique_visitors = Visitor.objects.count()

    top_pages = (
        PageView.objects
        .values('path')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    daily_visits = (
        PageView.objects
        .annotate(day=TruncDate('timestamp'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    return JsonResponse({
        'total_pageviews': total_pageviews,
        'unique_visitors': unique_visitors,
        'top_pages': list(top_pages),
        'daily_visits': list(daily_visits)
    })



@csrf_exempt
def track_funnel(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body or "{}")

        # -------------------------
        # SESSION SAFETY
        # -------------------------
        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key

        # -------------------------
        # VISITOR COOKIE
        # -------------------------
        visitor_id = request.COOKIES.get("visitor_id")

        if not visitor_id:
            visitor_id = str(uuid.uuid4())

        visitor, _ = Visitor.objects.get_or_create(
            visitor_id=visitor_id
        )

        session_obj, _ = Session.objects.get_or_create(
            session_key=session_key,
            defaults={"visitor": visitor}
        )

        # -------------------------
        # VALIDATION (IMPORTANT)
        # -------------------------
        funnel_name = data.get("funnel_name")
        step_number = data.get("step_number")
        step_name = data.get("step_name")

        if not funnel_name or step_number is None or not step_name:
            return JsonResponse({
                "error": "Missing funnel_name, step_number, or step_name"
            }, status=400)

        # -------------------------
        # CREATE EVENT
        # -------------------------
        FunnelEvent.objects.create(
            visitor=visitor,
            session=session_obj,
            funnel_name=funnel_name,
            step_number=int(step_number),
            step_name=step_name,
            metadata=data.get("metadata", {})
        )

        # -------------------------
        # RESPONSE
        # -------------------------
        response = JsonResponse({"status": "ok"})
        response.set_cookie(
            "visitor_id",
            visitor_id,
            max_age=60 * 60 * 24 * 365
        )

        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def analytics_dashboard(request):

    last_7_days = now() - timedelta(days=0)

    # ------------------------
    # BASIC STATS
    # ------------------------
    total_visitors = Visitor.objects.count()
    total_pageviews = PageView.objects.count()
    total_clicks = ClickEvent.objects.count()

    # ------------------------
    # TOP DATA
    # ------------------------
    top_pages = (
        PageView.objects.values("path")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    top_clicks = (
        ClickEvent.objects.values("label")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    top_countries = (
        Visitor.objects.values("country")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # ------------------------
    # DAILY PAGEVIEWS (7 DAYS)
    # ------------------------
    pageviews_by_day = (
        PageView.objects.filter(timestamp__gte=last_7_days)
        .extra(select={"day": "date(timestamp)"})
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    clicks_by_day = (
        ClickEvent.objects.filter(timestamp__gte=last_7_days)
        .extra(select={"day": "date(timestamp)"})
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    context = {
        "total_visitors": total_visitors,
        "total_pageviews": total_pageviews,
        "total_clicks": total_clicks,

        "top_pages": top_pages,
        "top_clicks": top_clicks,
        "top_countries": top_countries,

        "pageviews_by_day": list(pageviews_by_day),
        "clicks_by_day": list(clicks_by_day),
    }

    return render(request, "userprofile/analytics_dashboard.html", context)