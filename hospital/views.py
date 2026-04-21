from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import *
from .models import *
import uuid, json, requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def is_valid_queryparam(param):
    return param != '' and param is not None


def home_page(request):
	counties = County.objects.order_by('index')[:10]
	hospital = Hospital.objects.all()

	context = {
		'counties':counties,
		'hospital':hospital,
	}
	return render(request, 'hospital/home_page.html', context)



def county_centre(request,pk):
	county = get_object_or_404(County,pk=pk)
	county_name = (county.name).capitalize()
	qs = Hospital.objects.filter(county=county_name)

	name = request.GET.get('name')
	constituent = request.GET.get('constituent')
	ward = request.GET.get('ward')

	if is_valid_queryparam(name):
		qs = qs.filter(name__icontains=name)

	if is_valid_queryparam(constituent):
		qs = qs.filter(constituent__icontains=constituent)

	if is_valid_queryparam(ward):
		qs = qs.filter(ward__icontains=ward)

	context = {
		'county':county,
		'hospital':qs,
	}
	return render(request, 'hospital/county_centre.html', context)
