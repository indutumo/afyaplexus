from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import *
from .forms import *
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

def doctor_list(request):

    query = request.GET.get('q', '')
    hospital = request.GET.get('hospital', '')
    location = request.GET.get('location', '')

    doctors = Doctor.objects.all().order_by('-date')

    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(hospital__icontains=query)
        )

    if hospital:
        doctors = doctors.filter(hospital__icontains=hospital)

    if location:
        doctors = doctors.filter(location__icontains=location)

    # 🔥 AJAX RESPONSE
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for d in doctors[:50]:  # limit for performance
            data.append({
                "id": d.id,
                "name": f"{d.title} {d.name}",
                "hospital": str(d.hospital) if d.hospital else "-",
                "location": d.location or "-",
                "mobile": d.mobile_number,
                "email": d.email_address,
            })

        return JsonResponse({"doctors": data})

    # NORMAL PAGE LOAD (with pagination)
    paginator = Paginator(doctors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'doctor/doctor_list.html', {'page_obj': page_obj,'query': query})


# 👁 DETAIL
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)

    return render(request, 'doctor/doctor_detail.html', {
        'doctor': doctor
    })


#adding doctor
@login_required
def add_doctor(request):
    login = '/'
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()

            messages.success(request, "Doctor added successfully")
            return redirect('doctor_list')
    else:
        form = DoctorForm()

    return render(request, 'doctor/add_doctor.html', {'form': form})

#adding partner
def add_partner(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()

            messages.success(request, "Partner added successfully")
            return redirect('donate')
    else:
        form = PartnerForm()

    return render(request, 'hospital/get_involved.html', {'form': form})


#adding volunteer
def add_volunteer(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()

            messages.success(request, "Volunteer added successfully")
            return redirect('donate')
    else:
        form = VolunteerForm()

    return render(request, 'hospital/get_involved.html', {'form': form})

#adding patient
def add_patient(request):
    if request.method == 'POST':
        form = PatientSupportForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()

            messages.success(request, "Patient added successfully")
            return redirect('donate')
    else:
        form = PatientSupportForm()

    return render(request, 'hospital/get_involved.html', {'form': form})


def partner_list(request):
    query = request.GET.get('q', '')
    mobile_number = request.GET.get('mobile_number', '')
    contact_person = request.GET.get('contact_person', '')

    partner = Partner.objects.all().order_by('-date')

    if query:
        partner = partner.filter(
            Q(name__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(contact_person__icontains=query)
        )

    # 🔥 AJAX RESPONSE
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for d in partner[:50]:  # limit for performance
            data.append({
                "id": d.id,
                "name": f"{d.name}",
                "mobile": d.mobile_number,
                "contact_person": d.contact_person,
            })

        return JsonResponse({"partner": data})

    # NORMAL PAGE LOAD (with pagination)
    paginator = Paginator(partner, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'doctor/partner_list.html', {'page_obj': page_obj,'query': query})


def patient_list(request):
    query = request.GET.get('q', '')
    mobile_number = request.GET.get('mobile_number', '')
    support_type = request.GET.get('support_type', '')

    patient = PatientSupport.objects.all().order_by('-date')

    if query:
        patient = patient.filter(
            Q(name__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(support_type__icontains=query)
        )

    # 🔥 AJAX RESPONSE
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for d in patient[:50]:  # limit for performance
            data.append({
                "id": d.id,
                "name": f"{d.name}",
                "mobile": d.mobile_number,
                "support_type": d.support_type,
            })

        return JsonResponse({"patient": data})

    # NORMAL PAGE LOAD (with pagination)
    paginator = Paginator(patient, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'doctor/patient_list.html', {'page_obj': page_obj,'query': query})


def volunteer_list(request):
    query = request.GET.get('q', '')
    mobile_number = request.GET.get('mobile_number', '')
    area_of_interest = request.GET.get('area_of_interest', '')

    volunteer = Volunteer.objects.all().order_by('-date')

    if query:
        volunteer = volunteer.filter(
            Q(name__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(area_of_interest__icontains=query)
        )

    # 🔥 AJAX RESPONSE
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for d in volunteer[:50]:  # limit for performance
            data.append({
                "id": d.id,
                "name": f"{d.name}",
                "mobile": d.mobile_number,
                "area_of_interest": d.area_of_interest,
            })

        return JsonResponse({"volunteer": data})

    # NORMAL PAGE LOAD (with pagination)
    paginator = Paginator(volunteer, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'doctor/volunteer_list.html', {'page_obj': page_obj,'query': query})