from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from annoying.decorators import render_to
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def index(request):
    return HttpResponse("hi there")


@render_to('login.html')
def login_user(request):
    context = {'form_login': {}, 'wrong_login': False, 'wrong_username': False, 'form_create': {}, 'username_busy': False}
    if request.method == 'POST':
        try:
            action = request.POST['action']
            username = request.POST['username']
            password = request.POST['password']
            if action == 'login':
                context['form_login'] = request.POST
                try:
                    User.objects.get(username=username)
                    user = authenticate(username=username, password=password)
                    if user != None:
                        login(request, user)
                        print 'next: ', request.POST['next']
                        return redirect(reverse('app.views.home'))
                    else:
                        context['wrong_login'] = True
                except User.DoesNotExist:
                    context['wrong_username'] = True
            elif action == 'create':
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    User.objects.create_user(username, password=password)
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    print 'next: ', request.POST['next']
                    return redirect(reverse('app.views.home'))
                else:
                    context['username_busy'] = True
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
    return {}


