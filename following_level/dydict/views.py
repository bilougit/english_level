# -*- coding: utf-8 -*-
from random import randint

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib import messages

from dydict.models import Internaute
from dydict.forms import *
import tasks


class StaticTemplateView(TemplateView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StaticTemplateView, self).dispatch(*args, **kwargs)


class AboutView(StaticTemplateView):
    template_name = 'dydict/about.html'


class HelpView(StaticTemplateView):
    template_name = 'dydict/help.html'


@login_required
def listWords(request, page_number=1):
    #messages.info(request, u'test message')
    tpl_dict = tasks.words.delay(request.user, request.POST, request.method)
    if tpl_dict.get():
        words_page = tpl_dict.get()["words"]
        num_pages = words_page.num_pages
        page_number = int(page_number)
        current_page = page_number if page_number in range(1, num_pages + 1) \
                                   else 1
        words = words_page.page(current_page).object_list

        user = request.user
        word_form = tpl_dict.get()["word_form"]
        word_saved = tpl_dict.get()["word_saved"]
        tpl_vars = {'user': user,
                    'num_pages': words_page.num_pages,
                    'current_page': current_page,
                    'word_form': word_form,
                    'words': words,
                    'word_saved': word_saved,}

        if word_saved:
            tpl_vars['word'] = tpl_dict.get()["word"]

        return render(request, 'dydict/list_words.html',
                      tpl_vars)

def createUser(request):
    error = False
    if request.method == 'POST':
        registerform = RegisterForm(request.POST)
        if registerform.is_valid():
            username = registerform.cleaned_data['username']
            email = registerform.cleaned_data['email']
            password = registerform.cleaned_data['password']
            user = User.objects.create_user(username=username,
                        email=email,
                        password=password)

            internaute = Internaute(user=user)
            internaute.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/dictionary/show_words/')
    else:
        registerform = RegisterForm()
    return render(request, 'dydict/register.html', locals())

#@cache_page(60 * 15)
def user_login(request):
    error = False
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data["username"]
            password = loginform.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/dictionary/show_words/')
            else:
                error = True
    else:
        loginform = LoginForm()
    return render(request, 'dydict/login.html', locals())

def user_logout(request):
    logout(request)
    return redirect(reverse(user_login))
