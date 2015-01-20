from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from annoying.decorators import render_to
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from models import File
from forms import UploadFileForm
import requests
import datetime


SERVER_BASE_URL = 'http://localhost:8080/'


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
                'username': username,
                'password': password,
                'mail': request.POST.get('mail', None),
            }
            login_req = requests.post(SERVER_BASE_URL + 'login/' + action, data=data)
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
                    return redirect(reverse('app.views.home'), 0)
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
                    return redirect(reverse('app.views.home'), 0)
                else:
                    if login_status == 'username_busy':
                        context['username_busy'] = True
                    if login_status == 'invalid_mail':
                        context['invalid_mail'] = True
                    if login_status == 'mail_busy':
                        context['mail_busy'] = True
                    context['form_create'] = request.POST

        except requests.exceptions.ConnectionError:
            return render_to_response('down.html')
        except KeyError:
            return HttpResponseBadRequest()

    return context


@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse('app.views.login_user'))


@login_required
@render_to('home.html')
def home(request):
    location = request.GET.get('location', 0)
    try:
        login_req = requests.get(SERVER_BASE_URL + 'tree/show', \
            params={'id_usr': request.user.id, 'location': location})
        names, types, ids, parent = [e.split("=")[1] \
            for e in login_req.text.split('&')]
        names, types, ids = [e.split(",")[:-1] for e in [names, types, ids]]
    except requests.exceptions.ConnectionError:
        return render_to_response('down.html')

    files = [File(name=name, ftype=type, id=id) for name, type, id in \
        zip(names, types, ids)]
    form = UploadFileForm()
    return {'files': files, 'form': form, 'location': location, 'parent': parent}


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        location = request.POST['location']
        if form.is_valid():
            up_file = request.FILES['file']
            data = {
                'id_usr': request.user.id,
                'name': up_file.name,
                'type': up_file.content_type,
                'size': up_file.size,
                'location': location,
            }
            try:
                login_req = requests.post(SERVER_BASE_URL + 'file/upload', data=data)
            except requests.exceptions.ConnectionError:
                return render_to_response('down.html')
            login_status = login_req.text
        return redirect('/home?location=' + location)
    else:
        return HttpResponseBadRequest()

@login_required
def delete_file(request):
    if request.method == 'POST':
        data = {
            'id_file': request.POST['id'],
            'id_usr': request.user.id,
            }
        requests.post(SERVER_BASE_URL + 'file/delete', data=data)
        return redirect('/home?location=' + request.POST['location'])
    else:
        return HttpResponseBadRequest()


@login_required
def new_folder(request):
    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        try:
            requests.post(SERVER_BASE_URL + 'tree/update/new', data={ \
                'id_usr': request.user.id, 'location': location, 'name': name})
            return redirect('/home?location=' + location)
        except requests.exceptions.ConnectionError:
            return render_to_response('down.html')
    else:
        return HttpResponseBadRequest()

@csrf_exempt
@login_required
def move_file(request):
    if request.method == 'POST':
        try:
            data = {
                'id_usr': request.user.id,
                'dragged': request.POST['dragged_file_id'],
                'dropped': request.POST['dropped_file_id'],
                }
            requests.post(SERVER_BASE_URL + 'tree/update/move', data=data)
            return HttpResponse()
        except KeyError:
            return HttpResponseBadRequest()
