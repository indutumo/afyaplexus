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

class County(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Constituent(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	county = models.ForeignKey(County, related_name='constituent', on_delete=models.SET_NULL,null=True,blank=True)
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Ward(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	county = models.ForeignKey(County, related_name='ward', on_delete=models.SET_NULL,null=True,blank=True)
	constituent = models.ForeignKey(Constituent, related_name='ward', on_delete=models.SET_NULL,null=True,blank=True)
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Hospital(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	mobile_number = models.CharField(max_length=20,default="-")
	alternative_number = models.CharField(max_length=20,default="-")
	email_address = models.CharField(max_length=100,default="-")
	website =models.CharField(max_length=100,null=True,blank=True)
	centre_type = models.CharField(max_length=200,default='Public')
	mobile_pysical = models.CharField(max_length=20,default='Physical')
	county = models.CharField(max_length=20,null=True,blank=True)
	constituent = models.CharField(max_length=20,null=True,blank=True)
	location = models.TextField(null=True,blank=True)
	google_pin = models.CharField(max_length=50,null=True,blank=True)
	ward = models.CharField(max_length=20,null=True,blank=True)
	description = models.TextField(null=True,blank=True)
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='hospital', on_delete=models.SET_NULL,null=True,blank=True)
	status = models.CharField(max_length=20,default='active')

	def __str__(self):
		return self.name


class DailysisService(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	description = models.TextField(null=True,blank=True)
	cost = models.DecimalField(default=0.00, max_digits=1000, decimal_places=4)
	hospital = models.ForeignKey(Hospital, related_name='dailysisservice',on_delete=models.SET_NULL,null=True,blank=True)
	service_type = models.CharField(max_length=100)
	covered_by = models.CharField(max_length=20)
	schedule = models.CharField(max_length=20)
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='dailysisservice', on_delete=models.SET_NULL,null=True,blank=True)
	status = models.CharField(max_length=20,default='active')

	def __str__(self):
		return self.name


class HospitalRating(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	rating = models.CharField(max_length=200)
	comment = models.TextField(null=True,blank=True)
	hospital = models.ForeignKey(Hospital, related_name='hospitalrating',on_delete=models.SET_NULL,null=True,blank=True)
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='hospitalrating', on_delete=models.SET_NULL,null=True,blank=True)
	status = models.CharField(max_length=20,default='active')

	def __str__(self):
		return self.name