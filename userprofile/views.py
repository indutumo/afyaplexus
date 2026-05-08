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