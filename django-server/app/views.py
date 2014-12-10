from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from annoying.decorators import render_to
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import File
from forms import UploadFileForm
import requests
import datetime


SERVER_BASE_URL = 'http://localhost:8080/'

def index(request):
    return HttpResponse("hi there")


@render_to('login.html')
def login_user(request):
    context = {
        'form_login': {},
        'form_create': {},
        'wrong_login': False,
        'wrong_username': False,
        'username_busy': False,
        'invalid_mail': False,
        'mail_busy': False,
    }
    if request.method == 'POST':
        try:
            action = request.POST['action']
            username = request.POST['username']
            password = request.POST['password']
            data = {
                'option': action,
                'username': username,
                'password': password,
                'mail': request.POST.get('mail', None),
            }
            login_req = requests.post(SERVER_BASE_URL + 'login', data=data)
            login_status = login_req.text

            if action == 'connect':
                context['form_login'] = request.POST
                if login_status == 'ok':
                    try:
                        User.objects.get(username=username)
                    except User.DoesNotExist:
                        # User has not been created yet on Django server db
                        # first, get user id from main db
                        login_req = requests.get(SERVER_BASE_URL + 'login/data',
                            params={'mode': 'all', 'field': 'username', 'value': username})
                        id_usr, _, mail = [e.split("=")[1] for e in login_req.text.split('&')]
                        usr = User(id=id_usr, username=username, email=mail)
                        usr.set_password(password)
                        usr.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return redirect(reverse('app.views.home'))
                elif login_status == 'invalid_username':
                    context['wrong_username'] = True
                elif login_status == 'invalid_password':
                    context['wrong_login'] = True

            elif action == 'create':
                if login_status == 'ok':
                    # get user id from main db
                    login_req = requests.get(SERVER_BASE_URL + 'login/data',
                        params={'mode': 'single', 'data': 'id', 'field': 'username',
                        'value': username})
                    id_usr = login_req.text
                    usr = User(id=id_usr, username=username,
                        email=request.POST['mail'])
                    usr.set_password(password)
                    usr.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return redirect(reverse('app.views.home'))
                else:
                    if login_status == 'username_busy':
                        context['username_busy'] = True
                    if login_status == 'invalid_mail':
                        context['invalid_mail'] = True
                    if login_status == 'mail_busy':
                        context['mail_busy'] = True
                    context['form_create'] = request.POST

        except KeyError:
            return HttpResponseBadRequest

    return context


def logout_user(request):
    logout(request)
    return redirect(reverse('app.views.login_user'))


@login_required
@render_to('home.html')
def home(request):
    files = [
        File(name="fichier_1", ftype="txt", updated_date=datetime.datetime.now()),
        File(name="fichier_2", ftype="mp3", updated_date=datetime.datetime.now()),
        File(name="fichier_3", ftype="avi", updated_date=datetime.datetime.now()),
    ]
    form = UploadFileForm()
    return {'files': files, 'form': form}


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            up_file = request.FILES['file']
            print up_file.name, up_file.content_type, up_file.size
            
            username = request.POST['username']
            password = request.POST['password']
            data = {
                'option': 'upload',
                'username': username,
                'password': password,
                'mail': request.POST.get('mail', None),
            }
            login_req = requests.post(SERVER_BASE_URL + 'data', data=data)
            login_status = login_req.text
            print login_status




            return redirect(reverse('app.views.home'))
    else:
        return HttpResponseBadRequest

