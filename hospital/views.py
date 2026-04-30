from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import *
from .models import *
from page.models import Page
import uuid, json, requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

def is_valid_queryparam(param):
    return param != '' and param is not None


def home_page(request):
    counties = County.objects.order_by('index')[:10]
    hospital = Hospital.objects.all()
    blog = Page.objects.filter(featured=True).last()

    context = {
		'counties':counties,
		'hospital':hospital,
        'blog':blog,
	}
    return render(request, 'hospital/home_page.html', context)



def distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

def hospital_search(request):
    hospitals = Hospital.objects.all()

    query = request.GET.get('q')
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    # 🔍 TEXT SEARCH
    if query:
        hospitals = hospitals.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query)
        )

    # 📍 NEAR ME FILTER
    if user_lat and user_lng:
        user_lat = float(user_lat)
        user_lng = float(user_lng)

        nearby = []
        for h in hospitals:
            if h.latitude and h.longitude:
                dist = distance(user_lat, user_lng, h.latitude, h.longitude)
                if dist <= 20:  # 20km radius
                    h.distance = round(dist, 2)
                    nearby.append(h)

        hospitals = sorted(nearby, key=lambda x: x.distance)

    context = {
        'hospital': hospitals
    }
    print(context)
    return render(request, 'hospital/hospital_search.html', context)

@login_required
def add_centre(request):
    login_url = '/'
    if request.method == "POST":
        form = HospitalForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            mobile_number = form.cleaned_data['mobile_number']
            alternative_number = form.cleaned_data['alternative_number']
            location = form.cleaned_data['location']
            email_address = form.cleaned_data['email_address']
            website = form.cleaned_data['website']
            centre_type = form.cleaned_data['centre_type']
            county = form.cleaned_data['county']
            constituent = form.cleaned_data['constituent']
            ward = form.cleaned_data['ward']
            google_pin = form.cleaned_data['google_pin']
            description = form.cleaned_data['description']
            
            county = County.objects.filter(code=county).values_list('name', flat=True).last()
            hospital = Hospital(name=name,google_pin=google_pin,description=description,mobile_number=mobile_number,alternative_number=alternative_number,
            	location=location,email_address=email_address,website=website,centre_type=centre_type,county=county,constituent=constituent,ward=ward)
            hospital.save()
            messages.success(request, "Center created successfully.")
            return redirect('home_page')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HospitalForm()
    counties = County.objects.all()
    wards = Ward.objects.all()
    constituents = Constituent.objects.all()
    context = {
        'form': form,
        'counties':counties,
        'wards':wards,
        'constituents': constituents,
        }
    return render(request, 'hospital/center_form.html', context)



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



def centre_detail(request,pk):
    hospital = get_object_or_404(Hospital,pk=pk)
    dailysisservice = DailysisService.objects.filter(hospital=hospital)
    hospitalrating = HospitalRating.objects.filter(hospital=hospital)
    hospitalimage = HospitalImage.objects.filter(hospital=hospital)

    context = {
        'dailysisservice':dailysisservice,
        'hospitalrating':hospitalrating,
        'hospitalimage':hospitalimage,
        'hospital':hospital,
    }
    return render(request, 'hospital/centre_details.html', context)