from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from folders.models import Folder
from folders.utils import copy_folder
from users.models import UserAccount, RegistrationForm, SignInForm
from users.utils import *


@transaction.autocommit
def registration(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = UserAccount(email = form.cleaned_data['email'],
                           type = 1,
                           status=1,
                           username = form.cleaned_data['username'],
                           password = form.cleaned_data['password'],
                           on_announce_list = form.cleaned_data['on_announce_list'])
            user.save()
            login_user(request, user)
            copy_folder(get_object_or_404(Folder, user=settings.DEFAULT_USER_ID, default_folder=True), user)
    else:
        form = RegistrationForm()

    if request.is_logged_in:
        return render_to_response('register-confirm.html', context_instance=RequestContext(request))

    return render_to_response('register.html', { 'form': form }, context_instance=RequestContext(request))

def settings(request):
    return render_to_response('account-settings.html', context_instance=RequestContext(request))

##
#    This view is both responsible for logging in and logging out accounts.
#    Will also do a subsequent redirect if a return URL is provided.
def login(request, return_url=None, logout_requested=False):

    if logout_requested:
        logout_user(request)
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            try:
                user = UserAccount.objects.get(Q(username = form.cleaned_data['username'])
                                            | Q(email = form.cleaned_data['username'])
                                            , Q(password = form.cleaned_data['password']))
                login_user(request, user)
                HttpResponseRedirect(return_url or reverse('home'))
            except ObjectDoesNotExist:
                render_to_response('login.html', { 'form': form }, context_instance=RequestContext(request))

    else:
        form = SignInForm()

    if return_url:
        HttpResponseRedirect(return_url)
    else:
        return render_to_response('login.html', { 'form': form }, context_instance=RequestContext(request))
