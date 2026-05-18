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

    # --------------------------------
    # FILTERS
    # --------------------------------
    period = request.GET.get("period", "7d")

    if period == "24h":
        start_date = now() - timedelta(days=1)

    elif period == "30d":
        start_date = now() - timedelta(days=30)

    else:
        start_date = now() - timedelta(days=7)

    # --------------------------------
    # BASIC STATS
    # --------------------------------
    visitors = Visitor.objects.filter(
        first_seen__gte=start_date
    ).count()

    pageviews = PageView.objects.filter(
        timestamp__gte=start_date
    ).count()

    clicks = ClickEvent.objects.filter(
        timestamp__gte=start_date
    ).count()

    # --------------------------------
    # NEW VISITS
    # --------------------------------
    new_visits = Visitor.objects.filter(
        first_seen__gte=start_date
    ).count()

    # --------------------------------
    # RETURNING VISITS
    # --------------------------------
    revisit_count = Visitor.objects.filter(
        last_seen__gt=start_date
    ).exclude(
        first_seen__gte=start_date
    ).count()

    # --------------------------------
    # TOP PAGES
    # --------------------------------
    top_pages = (
        PageView.objects.filter(timestamp__gte=start_date)
        .values("path")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # --------------------------------
    # TOP CLICKS
    # --------------------------------
    top_clicks = (
        ClickEvent.objects.filter(timestamp__gte=start_date)
        .values("label")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # --------------------------------
    # MOST VISITED PAGE
    # --------------------------------
    top_page = (
        PageView.objects.filter(timestamp__gte=start_date)
        .values("path")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    # --------------------------------
    # MOST CLICKED ITEM
    # --------------------------------
    top_click = (
        ClickEvent.objects.filter(timestamp__gte=start_date)
        .values("label")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    # --------------------------------
    # COUNTRY STATS
    # --------------------------------
    country_stats = (
        Visitor.objects.filter(first_seen__gte=start_date)
        .values("country")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    # --------------------------------
    # DAILY PAGE TRENDS
    # --------------------------------
    trend_days = 7

    daily_pages = (
        PageView.objects.filter(
            timestamp__gte=now() - timedelta(days=trend_days)
        )
        .extra(select={"day": "date(timestamp)"})
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # --------------------------------
    # DAILY CLICK TRENDS
    # --------------------------------
    daily_clicks = (
        ClickEvent.objects.filter(
            timestamp__gte=now() - timedelta(days=trend_days)
        )
        .extra(select={"day": "date(timestamp)"})
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # --------------------------------
    # CONTEXT
    # --------------------------------
    context = {

        # KPI
        "visitors": visitors,
        "pageviews": pageviews,
        "clicks": clicks,
        "new_visits": new_visits,
        "revisit_count": revisit_count,

        # TOP STATS
        "top_page": top_page,
        "top_click": top_click,

        # TABLES
        "top_pages": list(top_pages),
        "top_clicks": list(top_clicks),

        # CHARTS
        "country_stats": list(country_stats),
        "daily_pages": list(daily_pages),
        "daily_clicks": list(daily_clicks),

        # FILTER
        "period": period,
    }

    return render(request,"userprofile/analytics_dashboard.html",context)


def visit_list(request):

    search = request.GET.get("search", "")

    visitors = Visitor.objects.all().order_by("-last_seen")

    if search:
        visitors = visitors.filter(
            Q(visitor_id__icontains=search) |
            Q(country__icontains=search) |
            Q(city__icontains=search) |
            Q(ip_address__icontains=search)
        )

    # Detect returning visitors
    visitor_data = []

    for visitor in visitors:
        is_returning = (
            visitor.last_seen - visitor.first_seen
        ) > timedelta(minutes=30)

        visitor_data.append({
            "visitor": visitor,
            "is_returning": is_returning
        })

    paginator = Paginator(visitor_data, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search
    }

    return render(
        request,
        "userprofile/visit_list.html",
        context
    )


def pageview_list(request):

    search = request.GET.get("search", "")
    method = request.GET.get("method", "")

    pageviews = PageView.objects.select_related("visitor").order_by("-timestamp")

    # ----------------------------
    # SEARCH FILTER
    # ----------------------------
    if search:
        pageviews = pageviews.filter(
            Q(path__icontains=search) |
            Q(view_name__icontains=search) |
            Q(referrer__icontains=search) |
            Q(visitor__visitor_id__icontains=search)
        )

    # ----------------------------
    # METHOD FILTER
    # ----------------------------
    if method:
        pageviews = pageviews.filter(method=method)

    # ----------------------------
    # PAGINATION
    # ----------------------------
    paginator = Paginator(pageviews, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "method": method,
    }

    return render(request, "userprofile/pageview_list.html", context)


def click_event_list(request):

    search = request.GET.get("search", "")
    event_type = request.GET.get("event_type", "")

    clicks = ClickEvent.objects.select_related("visitor").order_by("-timestamp")

    # --------------------------
    # SEARCH FILTER
    # --------------------------
    if search:
        clicks = clicks.filter(
            Q(label__icontains=search) |
            Q(page__icontains=search) |
            Q(event_type__icontains=search) |
            Q(visitor__visitor_id__icontains=search)
        )

    # --------------------------
    # EVENT TYPE FILTER
    # --------------------------
    if event_type:
        clicks = clicks.filter(event_type=event_type)

    # --------------------------
    # PAGINATION
    # --------------------------
    paginator = Paginator(clicks, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "event_type": event_type,
    }

    return render(
        request,
        "userprofile/click_event_list.html",
        context
    )