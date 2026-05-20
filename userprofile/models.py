from django.db import models
from django.utils import timezone
from datetime import datetime
from django.urls import reverse
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import datetime, uuid, decimal, requests
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
today = date.today()


def img_url(self, filename):
    hash_ = int(time.time())
    return "%s/%s/%s" % ("profile_pics", hash_, filename)


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True,blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    mobile_number=models.CharField(max_length=20,null=True,blank=True)
    user = models.ForeignKey(User, related_name='userprofilerole', on_delete=models.SET_NULL,null=True,blank=True)
    user_role = models.ForeignKey(Role, related_name='userprofilerole', on_delete=models.SET_NULL,null=True,blank=True)
    role_name = models.TextField(blank=True,null=True)
    user_added = models.ForeignKey(User,related_name='userprofilerole_added', on_delete=models.SET_NULL,null=True,blank=True)
    added_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20,default='active')
    user_removed = models.ForeignKey(User,related_name='userprofilerole_removed', on_delete=models.SET_NULL,null=True,blank=True)
    removed_datetime = models.DateTimeField(null=True,blank=True)
    terms_conditions = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.role_name is None:
            self.role_name = self.user_role.name                                                  
        super(UserProfileRole, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)



class Visitor(models.Model):
    visitor_id = models.CharField(max_length=120,unique=True)
    user = models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True,blank=True)
    visit_count = models.PositiveIntegerField(default=1)
    total_page_views = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True,blank=True)
    country = models.CharField(max_length=120,null=True,blank=True)
    region = models.CharField(max_length=120,null=True,blank=True)
    city = models.CharField(max_length=120,null=True,blank=True)
    timezone = models.CharField(max_length=120,null=True,blank=True)
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    user_agent = models.TextField(null=True,blank=True)
    browser = models.CharField(max_length=120,null=True,blank=True)
    browser_version = models.CharField(max_length=50,null=True,blank=True)
    operating_system = models.CharField(max_length=120,null=True,blank=True)
    device_type = models.CharField(max_length=50,null=True,blank=True)
    device_brand = models.CharField(max_length=120,null=True,blank=True)
    is_mobile = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_desktop = models.BooleanField(default=True)
    referrer = models.URLField(null=True,blank=True)
    referrer_domain = models.CharField(max_length=255,null=True,blank=True)
    landing_page = models.CharField(max_length=500,null=True,blank=True)
    utm_source = models.CharField(max_length=255,null=True,blank=True)
    utm_medium = models.CharField(max_length=255,null=True,blank=True)
    utm_campaign = models.CharField(max_length=255,null=True,blank=True)
    is_bot = models.BooleanField(default=False)
    bot_name = models.CharField(max_length=120,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_seen"]

    def __str__(self):

        if self.user:
            return f"{self.user.username}"

        location = ", ".join(
            filter(None, [self.city, self.country])
        )

        device = self.device_type or "Unknown Device"

        return f"{location} • {device}"


class Session(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=120, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.session_key


class PageView(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    path = models.CharField(max_length=500)
    full_url = models.TextField(null=True, blank=True)
    view_name = models.CharField(max_length=255, null=True, blank=True)
    method = models.CharField(max_length=20)
    referrer = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.path


class ClickEvent(models.Model):
    visitor = models.ForeignKey(Visitor,on_delete=models.CASCADE,related_name="click_events")
    session = models.ForeignKey(Session,on_delete=models.CASCADE,related_name="click_events")
    page = models.CharField(max_length=500,blank=True,null=True)
    page_title = models.CharField(max_length=255,blank=True,null=True)
    url = models.URLField(blank=True,null=True)
    referrer = models.URLField(blank=True,null=True)
    event_type = models.CharField(max_length=120)
    label = models.CharField(max_length=255,blank=True,null=True)
    element_type = models.CharField(max_length=50,blank=True,null=True)
    element_id = models.CharField(max_length=255,blank=True,null=True)
    css_class = models.TextField(blank=True,null=True)
    selector = models.TextField(blank=True,null=True)
    x = models.IntegerField(blank=True,null=True)
    y = models.IntegerField(blank=True,null=True)
    screen_width = models.IntegerField(blank=True,null=True)
    screen_height = models.IntegerField(blank=True,null=True)
    device_type = models.CharField(max_length=50,blank=True,null=True)
    browser = models.CharField(max_length=100,blank=True,null=True)
    operating_system = models.CharField(max_length=100,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return (
            f"{self.event_type} - "
            f"{self.label or 'Unknown'}"
        )


class SearchEvent(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    query = models.CharField(max_length=500)
    page = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)


class FunnelEvent(models.Model):
    visitor = models.ForeignKey("Visitor",on_delete=models.CASCADE)
    session = models.ForeignKey("Session",on_delete=models.CASCADE)
    funnel_name = models.CharField(max_length=120)
    # 🔥 IMPORTANT: numeric step for ordering
    step_number = models.IntegerField()
    step_name = models.CharField(max_length=120)
    # optional extra context (VERY useful later)
    metadata = models.JSONField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["funnel_name", "step_number", "timestamp"]
        indexes = [
            models.Index(fields=["funnel_name", "step_number"]),
            models.Index(fields=["visitor", "session"]),
        ]

    def __str__(self):
        return f"{self.funnel_name} - {self.step_number} ({self.step_name})"