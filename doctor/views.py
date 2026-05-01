from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Doctor
from .forms import DoctorForm


def doctor_list(request):
    query = request.GET.get('q')
    hospital = request.GET.get('hospital')
    location = request.GET.get('location')

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


# ➕ ADD
@login_required
def add_doctor(request):
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