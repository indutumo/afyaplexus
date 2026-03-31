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