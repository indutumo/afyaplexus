from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.views.generic import ListView, UpdateView, CreateView,DeleteView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
import uuid, json, requests
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string, get_template 
from django.template import Context, Template, RequestContext
from django.utils.crypto import get_random_string
from organization.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from pos.models import Receipts

def is_valid_queryparam(param):
    return param != '' and param is not None


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            u = form.cleaned_data['username']
            p = form.cleaned_data['password']
            user = authenticate(username=u, password=p)

            if user is not None:
                auth.login(request, user)
                if request.user.userprofile.cashier:
                    return redirect('pos_sales_dasboard')
                elif request.user.userprofile.discountloan_client:
                    return redirect('discountloan_dashboard')
                elif request.user.userprofile.hcm:
                    return redirect('hcm_maindashboard')
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, "Your username or password are incorrect !")
    else:
        form = UserLoginForm()
        print(form.errors)
    context = {
        'form':form
        }
    return render(request, 'registration/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')

def profile(request):
    return render(request, 'account/profile.html')

def register(request):
    if request.method=="POST":
        registration_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if registration_form.is_valid() and profile_form.is_valid():
            user = registration_form.save()
            profile =profile_form.save(commit=False)
            profile.user = user 
            profile.save()

            u = registration_form.cleaned_data['username']
            p = registration_form.cleaned_data['password1']
            user = authenticate(username=u, password=p)
            return redirect('user_list')
    else:
        registration_form = UserRegistrationForm()
        profile_form = UserProfileForm()

    context = {
        'registration_form':registration_form,
        'profile_form':profile_form
        }
    return render(request, 'account/register.html', context)


@login_required
def  user_list(request):
    login_url = '/'
    if request.user.userprofile.client:
        qs = UserProfile.objects.filter(organization__userprofile__user=request.user.pk).filter(client=True)
    else:
        qs = UserProfile.objects.all()


    name = request.GET.get('name')

    if is_valid_queryparam(name):
        qs = qs.filter(Q(first_name__icontains=name)
                       | Q(last_name__icontains=name)
                       ).distinct()

    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 30)

    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)

    context = {
        'user_list': qs,
        'name':name,
    }
    return render(request, "auth/user_list.html", context)


#user profile
@login_required
def view_profile(request, pk):
    login_url = '/'
    user_profile = get_object_or_404(UserProfile, pk=pk)
    user_role = UserProfileRole.objects.filter(user=user_profile.user,status='active')
    role = Role.objects.all()
    context = {
        'user_profile': user_profile,
        'user_role': user_role,
        'role': role,
        }
    return render(request, 'auth/user_detail.html', context)


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect(reverse('user_list'))
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/edit_profile.html', args)



class UserProfileUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/'
    redirect_field_name = 'auth/user_list.html'

    form_class = UserProfileForm

    model = UserProfile


def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=404)

def handler400(request, exception):
    return render(request, '400.html', status=404)

def handler403(request,exception):
    return render(request, '403.html', status=404)

def app(request):
    return redirect("/")


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            if request.user.userprofile.client:
                return redirect('dashboard')
            elif request.user.userprofile.discountloan_client:
                return redirect('discountloan_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    context = {
        'form':form
        }
    return render(request, 'account/password_change.html', context)


@login_required
def deactivate_user(request, pk):
    user = get_object_or_404(UserProfile,pk=pk)
    UserProfile.objects.filter(id=user.id).update(active=False)
    User.objects.filter(id=user.user.id).update(is_active = False)
    return redirect('user_detail', pk=user.pk)

@login_required
def activate_user(request, pk):
    user = get_object_or_404(UserProfile,pk=pk)
    UserProfile.objects.filter(id=user.id).update(active=True)
    User.objects.filter(id=user.user.id).update(is_active = True)
    return redirect('user_detail', pk=user.pk)


def register_user(request):
    if request.method=="POST":
        organization = request.user.userprofile.organization
        registration_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST,request.FILES)
        if registration_form.is_valid() and profile_form.is_valid():
            first_name = registration_form.cleaned_data['first_name']
            last_name = registration_form.cleaned_data['last_name']
            username = registration_form.cleaned_data['username']
            email = registration_form.cleaned_data['email']
            password_new = get_random_string(length=10)
            print(password_new)
            password = make_password(password_new)
            user = User(first_name=first_name,last_name=last_name,username=username,email=email,password=password)

            mobile_number = profile_form.cleaned_data['mobile_number']
            organization = profile_form.cleaned_data['organization']
            if organization is None:
                organization = request.user.userprofile.organization
            branch = profile_form.cleaned_data['branch']
            department = profile_form.cleaned_data['department']
            cashier = profile_form.cleaned_data['cashier']
            account = profile_form.cleaned_data['account']
            pos = profile_form.cleaned_data['pos']
            sales = profile_form.cleaned_data['sales']
            procurement_approval = profile_form.cleaned_data['procurement_approval']
            manager = profile_form.cleaned_data['manager']
            procurement = profile_form.cleaned_data['procurement']
            admin = profile_form.cleaned_data['admin']
            create_invoice = profile_form.cleaned_data['create_invoice']
            hr = profile_form.cleaned_data['hr']
            billing = profile_form.cleaned_data['billing']
            total_list = profile_form.cleaned_data['total_list']
            quote_delivery = profile_form.cleaned_data['quote_delivery']
            invoice_date = profile_form.cleaned_data['invoice_date']
            multi_branch = profile_form.cleaned_data['multi_branch']
            
            #discount loan roles
            contract = profile_form.cleaned_data['contract']
            onboarding = profile_form.cleaned_data['onboarding']
            termloan = profile_form.cleaned_data['termloan']
            discount_loan = profile_form.cleaned_data['discount_loan']
            operation = profile_form.cleaned_data['operation']
            operation_manager = profile_form.cleaned_data['operation_manager']
            finance = profile_form.cleaned_data['finance']
            finance_manager = profile_form.cleaned_data['finance_manager']
            client_operation = profile_form.cleaned_data['client_operation']
            client_operation_manager = profile_form.cleaned_data['client_operation_manager']
            client_finance = profile_form.cleaned_data['client_finance']
            pooled_factoring = profile_form.cleaned_data['pooled_factoring']
            discountloan_client = profile_form.cleaned_data['total_list']
            discountloan_buyer = profile_form.cleaned_data['discountloan_buyer']
            funder = profile_form.cleaned_data['funder']


            if User.objects.filter(email=email).exclude(username=username):
                messages.error(request, 'Your email must be unique.')
            elif User.objects.filter(username=username):
                messages.error(request, 'Your username must be unique.')
            elif UserProfile.objects.filter(mobile_number=mobile_number):
                messages.error(request, 'Your mobile number must be unique.')
            else:
                user.save()
                profile = UserProfile(user=user,mobile_number=mobile_number,organization=organization,branch=branch,department=department,
                    cashier=cashier,account=account,pos=pos,sales=sales,procurement_approval=procurement_approval,manager=manager,
                    procurement=procurement,admin=admin,first_name=first_name,last_name=last_name,username=username,create_invoice=create_invoice,
                    hr=hr,billing=billing,total_list=total_list,quote_delivery=quote_delivery,invoice_date=invoice_date,multi_branch=multi_branch,
                    contract=contract,onboarding=onboarding,termloan=termloan,discount_loan=discount_loan,operation=operation,
                    operation_manager=operation_manager,finance=finance,finance_manager=finance_manager,client_operation=client_operation,
                    client_operation_manager=client_operation_manager,client_finance=client_finance,pooled_factoring=pooled_factoring,
                    discountloan_client=discountloan_client,discountloan_buyer=discountloan_buyer,funder=funder)
                profile.save()

                try:
                    #email notification
                    subject = 'Login Details'
                    context = {'password_new': password_new,'username':username,'first_name':first_name}
                    message = get_template('account/user_email.html').render(context)
                    email = EmailMessage(
                        "Login Details", message,"Zola Technologies Limited", [email],['isaacndutumo@gmail.com']
                    )
                    email.content_subtype = "html" 
                    email.send()

                    #sms notification
                    message = "Dear " +  str(first_name) + " , "+ "your username and password is " + " "+ str(username) +" ," + str(password_new) + " " + "to login go to http://192.168.1.10"
                    url = 'https://ujumbesms.co.ke/api/messaging'
                    headers = {'x-authorization': 'ZTQ2NjhkMGMxYjdiYTNhN2RlYzkxNzY1MGQwZmQ5',
                                'email': 'zolatechnologies@gmail.com'
                               }
                    body = {
                            "data": [
                                {
                                    "message_bag": {
                                        "numbers": mobile_number,
                                        "message": message,
                                        "sender": "ZOLA",
                                        "source_id":"12345_a unique_identifier_for_each_message",
                                        "delivery_report_endpoint":"https://you_link_to_post_the_delivery_report" 
                                    }
                                }
                            ]
                        }
                    response = requests.post(url=url, json=body, headers=headers)
                    text = "user" + " " + str(first_name) + " , "+ "new password "
                    Outbox.objects.create(organization=request.user.userprofile.organization,phone=mobile_number,text=text,
                        messageId='success',status='success')
                except:
                    pass

                return redirect('user_list')
        else:
            print(registration_form.errors)
            print(profile_form.errors)
    else:
        registration_form = UserForm()
        profile_form = UserProfileForm()

    organization = request.user.userprofile.organization
    branch = Branch.objects.filter(organization=organization).all()
    department = Department.objects.filter(organization=organization).all()
    contract = Contract.objects.filter(organization=organization)
    context = {
        'registration_form':registration_form,
        'profile_form':profile_form,
        'organization':organization,
        'branch':branch,
        'department':department,
        'contract': contract,
        }
    return render(request, 'account/new_users_form.html', context)


def send_mail_test(request):
    #email notification
    subject = 'Login Details'
    password_new = 'Test'
    username = 'Ndutumo'
    first_name = 'Isaac'
    context = {'password_new': password_new,'username':username,'first_name':first_name}
    message = get_template('account/user_email.html').render(context)
    email = EmailMessage(
        "Login Details", message,"Zola Technologies", ['isaacndutumo@gmail.com']
    )
    email.content_subtype = "html" 
    email.send()


def zolatechnologies(request):
    return redirect("https://zolatechnologies.com")


def whatsapp_chat(request):
    return redirect("https://api.whatsapp.com/send?phone=254735296707&text=")


def waiter_logout(request):
    logout(request)
    return redirect('waiter_login')

def waiter_login(request):
    if request.method == "POST":
        form = WaiterLoginForm(request.POST)
        if form.is_valid():
            p = form.cleaned_data['password']
            u = Waiter.objects.filter(pin=p).values_list('username', flat=True).last()
            print(u)
            user = authenticate(username=u, password=p)
            print(user)

            if user is not None:
                auth.login(request, user)
                receipt = Receipts.objects.filter(organization=request.user.userprofile.organization).order_by('datetime').values_list('id',flat=True).last()
                return redirect('menu_category_dashboard', receipt)
            else:
                messages.error(request, "Your pin is  invalid !")
    else:
        form = WaiterLoginForm()
        print(form.errors)
    waiter = UserProfile.objects.filter(waiter=True)
    context = {
        'form':form,
        'waiter':waiter,
        }
    return render(request, 'registration/waiter_login.html',context)



@login_required
def add_issue(request):
    login_url = '/'
    if request.method == "POST":
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            issue = form.cleaned_data['issue']
            capture = form.cleaned_data['capture']

            issue = Issue(organization=request.user.userprofile.organization,user=request.user,
                subject=subject,issue=issue,capture=capture)
            issue.save()
            return redirect('issue_list')
        else:
            print(form.errors)

    else:
        form = IssueForm()
    context = {
        'form':form
        }
    return render(request, 'support/issue_form.html', context)


@login_required
def  issue_list (request):
    login_url = '/'
    
    qs = Issue.objects.filter(organization=request.user.userprofile.organization).order_by('-datetime')

    subject = request.GET.get('subject')

    if is_valid_queryparam(subject):
        qs = qs.filter(subject__icontains=subject)

    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 4)

    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)

    context = {
        'issue_list': qs,
        'subject':subject,
    }
    return render(request, "support/issue_list.html", context)


@login_required
def add_response(request,pk):
    login_url = '/'
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == "POST":
        form = ResposeForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.cleaned_data['response']
            capture = form.cleaned_data['capture']

            response = Respose(organization=request.user.userprofile.organization,user=request.user,
                issue=issue,response=response,capture=capture)
            response.save()
            return redirect('issue_details', pk=issue.pk)
        else:
            print(form.errors)

    else:
        form = ResposeForm()
    context = {
        'form':form
        }
    return render(request, 'support/issue.html', context)



@login_required
def add_client_response(request,pk):
    login_url = '/'
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == "POST":
        form = ClientResposeForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.cleaned_data['response']
            capture = form.cleaned_data['capture']

            clientresponse = ClientRespose(organization=request.user.userprofile.organization,user=request.user,
                issue=issue,response=response,capture=capture)
            clientresponse.save()
            return redirect('issue_details', pk=issue.pk)
        else:
            print(form.errors)

    else:
        form = ClientResposeForm()
    context = {
        'form':form
        }
    return render(request, 'support/issue.html', context)



class IssueDetailView(DetailView,LoginRequiredMixin):
    login_url = '/'
    model = Issue
    template_name ='support/issue.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(IssueDetailView, self).get_context_data(*args, **kwargs) 
        ctx['client_response'] = ClientRespose.objects.filter(issue=self.kwargs['pk'])
        ctx['response'] = Respose.objects.filter(issue=self.kwargs['pk'])

        return ctx


@login_required
def userdetails_edit(request,pk):
    login_url = '/'
    user_profile = get_object_or_404(UserProfile,pk=pk)
    if request.method=="POST":
        form = UserProfileForm(request.POST,request.FILES)
        if  form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            mobile_number = form.cleaned_data['mobile_number']
            department = form.cleaned_data['department']
            admin = form.cleaned_data['admin']
            cashier = form.cleaned_data['cashier']
            procurement_approval = form.cleaned_data['procurement_approval']
            procurement = form.cleaned_data['procurement']
            account = form.cleaned_data['account']
            sales = form.cleaned_data['sales']
            pos = form.cleaned_data['pos']
            manager = form.cleaned_data['manager']
            create_invoice = form.cleaned_data['create_invoice']
            hr = form.cleaned_data['hr']
            billing = form.cleaned_data['billing']
            total_list = form.cleaned_data['total_list']
            quote_delivery = form.cleaned_data['quote_delivery']
            invoice_date = form.cleaned_data['invoice_date']
            multi_branch = form.cleaned_data['multi_branch']

            UserProfile.objects.filter(id=user_profile.id).update(mobile_number=mobile_number,department=department,admin=admin,cashier=cashier,
                procurement_approval=procurement_approval,procurement=procurement,account=account,sales=sales,pos=pos,manager=manager,create_invoice=create_invoice,
                hr=hr,billing=billing,total_list=total_list,quote_delivery=quote_delivery,invoice_date=invoice_date,multi_branch=multi_branch)
            User.objects.filter(id=user_profile.user.id).update(first_name=first_name,last_name=last_name,username=username,email=email)

            return redirect('user_detail', pk=user_profile.pk)
        else:
            print(form.errors)

    else:
        form = UserProfileForm()

    department = Department.objects.filter(organization=request.user.userprofile.organization)
    context = {
        'form':form,
        'user_profile':user_profile,
        'department':department,
        }
    return render(request, 'account/user_edit.html', context)


@login_required
def send_patient_notification(request):
    organization = request.user.userprofile.organization
    patient = PatientVisit.objects.filter(organization=organization).filter(status=True).values_list('patient', flat=True)
    for patient in patient:
        print(patient)
        patient_id = PatientVisit.objects.filter(organization=organization).filter(patient=patient).values_list('patient', flat=True).last()
        patient_name = Patient.objects.filter(id=patient_id).values_list('name', flat=True).last()
        mobile_number = Patient.objects.filter(id=patient_id).values_list('mobile_number', flat=True).last()
        date = PatientVisit.objects.filter(patient=patient_id).values_list('appointment_date', flat=True).last()
        procedure = PatientVisit.objects.filter(patient=patient_id).values_list('procedure', flat=True).last()

        message = PatientNotification.objects.filter(organization=organization).filter(name='Reminder').values_list('message', flat=True).last()
        message_test = "Dear "+ str(patient_name) +","+"Your next appointment is on" +" "+  str(date) +" "+ "for" +" "+ str(procedure) +". "+"For any clarification calls or whatsapp us: 0713469929. Thanks."
        #sms notification
        url = 'https://ujumbesms.co.ke/api/messaging'
        headers = {'x-authorization': 'ZTQ2NjhkMGMxYjdiYTNhN2RlYzkxNzY1MGQwZmQ5',
                    'email': 'zolatechnologies@gmail.com'
                   }
        body = {
                "data": [
                    {
                        "message_bag": {
                            "numbers": mobile_number,
                            "message": message_test,
                            "sender": "ZOLA",
                            "source_id":"12345_a unique_identifier_for_each_message",
                            "delivery_report_endpoint":"https://you_link_to_post_the_delivery_report" 
                        }
                    }
                ]
            }
        response = requests.post(url=url, json=body, headers=headers)
        Outbox.objects.create(organization=request.user.userprofile.organization,phone=mobile_number,text=message,
            messageId='success',status='success')

    return redirect("patient_notification")


@login_required
def sms_notification_list(request):
    login_url = '/'
    organization = request.user.userprofile.organization
    qs = Outbox.objects.filter(organization=organization).order_by('-date')

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    request.session['date_min'] = date_min
    request.session['date_max'] = date_max

    if is_valid_queryparam(date_min):
        qs = qs.filter(date__date__gte=date_min)

    if is_valid_queryparam(date_max):
        qs = qs.filter(date__date__lte=date_max)

    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 10)

    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)

    context = {
        'sms_notification':qs,
        'date_min':date_min,
        'date_max':date_max,
    }
    return render(request, "account/sms_notification.html", context)


#change the branch 
@login_required
def change_branch(request):
    if request.method == "POST":
        form = ChangeForm(request.POST)
        if form.is_valid():
            branch = form.cleaned_data['branch']
            UserProfile.objects.filter(user=request.user).update(branch=branch)
            if request.user.userprofile.cashier:
                return redirect('pos_sales_dasboard')
            else:
                return redirect('pos_sales_dasboard')
    else:
        form = ChangeForm()
        print(form.errors)
    context = {
        'form':form
        }
    return render(request, 'registration/change_branch.html', context)



def check_username(request):
    username = request.POST.get('username')
    print(username)
    if User.objects.filter(username=username).exists():
        return HttpResponse("<div style='color: red;'>This username already exists !</div>")
    elif not username:
        return HttpResponse("")
    else:
        return HttpResponse("<div style='color: green;'> This username is available. </div>")


#change organization
@login_required
def change_organization(request):
    login_url = '/'
    if request.method == "POST":
        form = ParentOrganizationForm(request.POST)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            UserProfile.objects.filter(user=request.user).update(organization=parent)
            return redirect('organization_list')
        else:
            print(form.errors)
    else:
        form = ParentOrganizationForm()
    context = {
        'form': form
        }
    return render(request, 'organization/department_list.html', context)


@login_required
def send_client_notification(request):
    login_url = '/'
    if request.method == "POST":
        form = OutboxForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']

            organization = request.user.userprofile.organization
            client = Client.objects.filter(organization=organization).filter(status='active').values_list('id', flat=True)
            for client in client:
                print(client)
                name = Client.objects.filter(id=client).values_list('contact_person_name', flat=True).last()
                mobile_number = Client.objects.filter(id=client).values_list('contact_person_number', flat=True).last()
                #mobile_number = '0713469929'

                message_text = "Dear "+ str(name) +","+ str(message)
                #sms notification
                if mobile_number is not None:
                    url = 'https://sms.textsms.co.ke/api/services/sendsms/'
                    body = {
                                "apikey":"3e5d2c09da07df2df80768d7ae9ed2b6",
                                "partnerID":"9738",
                                "message": message_text,
                                "shortcode":"MULTSIDE",
                                "mobile": mobile_number,
                            }
                    response = requests.post(url=url, json=body)
                    Outbox.objects.create(organization=request.user.userprofile.organization,phone=mobile_number,text=message_text,
                        messageId='success',status='success',sender_id='MULTSIDE')

            return redirect('sms_notification_list')
        else:
            print(form.errors)
    else:
        form = OutboxForm()
    context = {
        'form': form
        }
    return render(request, 'account/sms_notification.html', context)


@login_required
def add_userprofilerole(request,pk):
    userprofile = get_object_or_404(UserProfile, pk=pk)
    login_url = '/'
    if request.method == "POST":
        form = UserProfileRoleForm(request.POST, request.FILES)
        if form.is_valid():
            user_role = form.cleaned_data['user_role']

            roles = UserProfileRole.objects.filter(user=userprofile.user,user_role=user_role,status='active')
            if not roles:
                UserProfileRole.objects.create(user=userprofile.user,userprofile=userprofile,organization=userprofile.organization,
                    legalentity=userprofile.legalentity,user_role=user_role,user_added=request.user)

                role_name = Role.objects.filter(id=user_role.id).values_list('name', flat=True).last()
                if role_name == 'Human Resource': 
                    UserProfile.objects.filter(id=userprofile.id).update(employee=True,human_resource=True)
                elif role_name == 'Payroll Manager':
                    UserProfile.objects.filter(id=userprofile.id).update(employee=True,payroll_manager=True)
                elif role_name == 'Recruiter':
                    UserProfile.objects.filter(id=userprofile.id).update(employee=True,recruiter=True)
                else:
                    UserProfile.objects.filter(id=userprofile.id).update(employee=True,recruiter=True)

            return redirect('user_detail', pk=userprofile.pk)
        else:
            print(form.errors)

    else:
        form = UserProfileRoleForm()
    context = {
        'form':form
        }
    return render(request, 'support/issue_form.html', context)

@login_required
def remove_userrole(request, pk):
    login_url = '/'
    userprofilerole = get_object_or_404(UserProfileRole,pk=pk)
    UserProfileRole.objects.filter(id=userprofilerole.id).update(status='inactive',user_removed=request.user,
        removed_datetime=datetime.now())

    role_name = Role.objects.filter(id=userprofilerole.user_role.id).values_list('name', flat=True).last()
    if role_name == 'Human Resource': 
        UserProfile.objects.filter(id=userprofilerole.userprofile.id).update(human_resource=False)
    elif role_name == 'Payroll Manager':
        UserProfile.objects.filter(id=userprofilerole.userprofile.id).update(payroll_manager=False)
    elif role_name == 'Recruiter':
        UserProfile.objects.filter(id=userprofilerole.userprofile.id).update(recruiter=False)

    return redirect('user_detail', pk=userprofilerole.userprofile.pk)