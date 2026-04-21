from django.db import models
from django.utils import timezone
from django.urls import reverse
from datetime import date, datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User
import uuid, datetime, decimal, json, requests
from django.db.models import Sum, Avg, F, Q
from django.core.files import File
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.utils.timezone import localtime
today = date.today()
current_month = today.month
current_year = today.year
today = date.today()

class Page(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	page_type = models.CharField(max_length=20,default='Normal')
	status = models.CharField(max_length=20,default='active')
	content = models.TextField()
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='page', on_delete=models.SET_NULL,null=True,blank=True)
	rating = models.CharField(max_length=20,default=1)

	def __str__(self):
		return self.name


class PageAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    page = models.ForeignKey(Page,related_name='hcmresponse',on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User,related_name='hcmresponse',on_delete=models.SET_NULL,null=True,blank=True)
    attachment = models.FileField(upload_to='hcmresponse/%Y/%m/%d/'')/%Y/%m/%d/',blank=True,null=True)

    def __str__(self):
    	return str(self.page)

class PageComment(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	rating = models.CharField(max_length=200)
	comment = models.TextField(null=True,blank=True)
	page = models.ForeignKey(Page, related_name='pagecomment',on_delete=models.SET_NULL,null=True,blank=True)
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='pagecomment', on_delete=models.SET_NULL,null=True,blank=True)
	status = models.CharField(max_length=20,default='active')

	def __str__(self):
		return str(self.page)