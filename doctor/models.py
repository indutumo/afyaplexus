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

class Doctor(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	mobile_number = models.CharField(max_length=20,default="-")
	alternative_number = models.CharField(max_length=20,default="-")
	email_address = models.CharField(max_length=100,default="-")
	location = models.CharField(max_length=50,default='-')
	license_number = models.CharField(max_length=50,null=True,blank=True)
	license = models.FileField(upload_to="license/%Y/%m/%d",null=True,blank=True)
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='doctor', on_delete=models.SET_NULL,null=True,blank=True)
	account = models.ForeignKey(User, related_name='doctor_account', on_delete=models.SET_NULL,null=True,blank=True)
	status = models.CharField(max_length=20,default='active')
	title = models.CharField(max_length=250,default='DR.')
	hospital = models.CharField(max_length=250,null=True,blank=True)
	profile_picture = models.FileField(upload_to="profile/%Y/%m/%d",null=True,blank=True)

	def __str__(self):
		return self.name


class Partner(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	contact_person = models.CharField(max_length=200)
	mobile_number = models.CharField(max_length=20)
	email_address = models.CharField(max_length=100)
	partnership_type = models.CharField(max_length=200,default='Healthcare Partnership')
	date = models.DateField(default=timezone.now)
	status = models.CharField(max_length=50,default='Pending')
	notes = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name

class PatientSupport(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	mobile_number = models.CharField(max_length=20)
	email_address = models.CharField(max_length=100)
	support_type = models.CharField(max_length=200,default='Monetary Donation')
	contact_method = models.CharField(max_length=200,default='Phone')
	date = models.DateField(default=timezone.now)
	status = models.CharField(max_length=50,default='Pending')
	notes = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name


class Volunteer(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	mobile_number = models.CharField(max_length=20)
	email_address = models.CharField(max_length=100)
	area_of_interest = models.CharField(max_length=200,default='Community Outreach')
	date = models.DateField(default=timezone.now)
	status = models.CharField(max_length=50,default='Pending')
	notes = models.TextField(null=True,blank=True)

	def __str__(self):
		return self.name