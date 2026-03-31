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

class Patient(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
	name = models.CharField(max_length=200)
	mobile_number = models.CharField(max_length=20,default="-")
	alternative_number = models.CharField(max_length=20,default="-")
	email_address = models.CharField(max_length=100,default="-")
	location = models.CharField(max_length=50,default='-')
	google_pin = models.CharField(max_length=50,null=True,blank=True)
	date_of_birth = models.DateField(null=True,blank=True)
	age =models.CharField(max_length=10,null=True,blank=True)
	type_of_dailysis = models.CharField(max_length=200,default='Normal')
	need_help = models.BooleanField(default=False)
	date = models.DateField(default=timezone.now)
	user = models.ForeignKey(User, related_name='patient', on_delete=models.SET_NULL,null=True,blank=True)
	account = models.ForeignKey(User, related_name='patient_account', on_delete=models.SET_NULL,null=True,blank=True)
	status = models.CharField(max_length=20,default='active')

	def __str__(self):
		return self.name