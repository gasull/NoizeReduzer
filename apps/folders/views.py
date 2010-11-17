from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from folders import forms as folder_forms
from folders import models as folder_models
from folders import utils
from users.models import UserAccount
from users.utils import login_user
from helper.pager import Pager
from django.db import transaction
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def _folder_edit_form(folder, sub_feed_id=0):
    return folder_forms.FolderEditForm({'name': folder.name,
                           'days_old_limit': folder.days_old_limit,
                           'items_per_page': folder.items_per_page,
                           'subscription_feed_id': sub_feed_id
                          })

def _create_anonymous_user(request):
    user = UserAccount(type=1, status=1)
    user.save()
    login_user(request,user)
    return utils.copy_folder(get_object_or_404(folder_models.Folder, user=settings.DEFAULT_USER_ID, default_folder=True), user)


##
# Handles folder edits, along with providing a refreshed
# rendering of folder items (for the purpose of AJAX requests)
# TODO:  correctly display form submission errors
@transaction.autocommit
def folder_edit(request, folder_id,page=1):
    if not request.is_logged_in:
        folder = _create_anonymous_user(request)
        folder_id = folder.id
    else:
        folder = get_object_or_404(folder_models.Folder, pk=folder_id)

    subscription_feed_id = None
    if request.method == 'POST':
        form = folder_forms.FolderEditForm(request.POST)
        if form.is_valid():
#            if request.user_account.id == settings.DEFAULT_USER_ID
            rawfeed_id = form.cleaned_data['raw_feed_id']
            folder.name = form.cleaned_data['name']
            folder.items_per_page = int(form.cleaned_data['items_per_page'])
            folder.days_old_limit = int(form.cleaned_data['days_old_limit'])
            folder.save()
    pager = Pager(page_number=int(page), limit=folder.items_per_page, total_count=200)
    if subscription_feed_id > 0:
        sub_feed = folder_models.SubscriptionFeed.objects.get(rawfeed=rawfeed_id,folder=folder.id)
        return render_to_response('feed-items-snippet.html',
                                    {'sub_feed': sub_feed,
                                    'selected_folder': folder,
                                    },
                                    context_instance=RequestContext(request))
    return render_to_response('feed-items-snippet.html',
                              {'selected_folder': folder,
                               'feed_items': utils.get_folder_feed_items(folder, pager.start, pager.limit),
                               }, context_instance=RequestContext(request))

##
# Displays the selected folder.  If the user is not logged in
# then display the default folder.  It adds the feed if it's in
# the request.
@transaction.autocommit
def folder_render(request, folder_id=None, page=1):
    folder_add_form, feed_add_form, selected_folder = None, None, None

    if not request.is_logged_in and request.method == 'POST':
        selected_folder = _create_anonymous_user(request)
        folder_id = selected_folder.id
        user_id = request.user_account.id
    elif not request.is_logged_in:
        user_id = settings.DEFAULT_USER_ID
    else:
        user_id = request.user_account.id

    if folder_id and not selected_folder:
        selected_folder = get_object_or_404(folder_models.Folder, pk=int(folder_id))
    else:
        selected_folder = get_object_or_404(folder_models.Folder, user=user_id, default_folder=True)

    pager = Pager(page_number=int(page), limit=selected_folder.items_per_page, total_count=selected_folder.item_count)

    # On  post back, check for feed add and folder add actions
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'feed_add':
            feed_add_form = folder_forms.FeedAddForm(request.POST)
            if feed_add_form.is_valid():
                try:
                    utils.add_feed(selected_folder, feed_add_form.cleaned_data['url'])
                except utils.CannotParseFeed:
                    pass #FIXME:Ticket #42. Right now fails silently
        elif action == 'folder_add':
            folder_add_form = folder_forms.FolderAddForm(request.POST)
            if folder_add_form.is_valid():
                selected_folder = folder_models.Folder()
                selected_folder.user = UserAccount.objects.get(id=user_id)
                selected_folder.name = folder_add_form.cleaned_data['name']
                selected_folder.default_folder = False
                selected_folder.save()
                HttpResponseRedirect(reverse('folder_render', args=[selected_folder.id, selected_folder.name]))
        elif action == 'feed_delete' and request.POST.has_key('feed_id'):
            rawfeed_id = int(request.POST['feed_id'])
            feed = folder_models.SubscriptionFeed.objects.get(rawfeed=rawfeed_id,folder=selected_folder.id)
            feed.delete()
        elif action == 'feed_edit' and request.POST.has_key('feed_id') and request.POST.has_key('feed_name'):
            rawfeed_id = int(request.POST['feed_id'])
            feed = folder_models.SubscriptionFeed.objects.get(rawfeed=rawfeed_id,folder=selected_folder.id)
            feed.name = request.POST['feed_name']
            feed.save()
        elif action == 'folder_delete' and not selected_folder.default_folder:
            selected_folder.delete()
            selected_folder = get_object_or_404(folder_models.Folder, user=user_id, default_folder=True)

    if not feed_add_form:
        feed_add_form = folder_forms.FeedAddForm()
    if not folder_add_form:
        folder_add_form = folder_forms.FolderAddForm()

    return render_to_response('folder-render.html',
                              {'selected_folder': selected_folder,
                               'folders': folder_models.Folder.objects.filter(user=user_id),
                               'folder_edit_form': _folder_edit_form(selected_folder),
                                'folder_add_form': folder_add_form,
                                'feed_add_form': feed_add_form,
                                'feed_items': utils.get_folder_feed_items(selected_folder, pager.start, pager.limit),
                                'pager': pager
                                },
                               context_instance=RequestContext(request))

##
# Renders only one feed on the screen.
def feed_render(request, folder_id, subscription_feed_id, page=1):
    selected_folder = _get_folder(request, folder_id)
    sub_feed = folder_models.SubscriptionFeed.objects.get(id=subscription_feed_id)
    pager = Pager(page_number=int(page), limit=selected_folder.items_per_page, total_count=sub_feed.item_count)
    selected_folder.start = pager.start
    return render_to_response('folder-render.html',
                              {'sub_feed': sub_feed,
                               'folders': folder_models.Folder.objects.filter(user=selected_folder.user),
                               'selected_folder': selected_folder,
                               'folder_edit_form': _folder_edit_form(selected_folder, sub_feed.rawfeed.id),
                               'folder_add_form': folder_forms.FolderAddForm(),
                               'feed_add_form': folder_forms.FolderAddForm(),
                               'feed_items': utils.get_feed_items(sub_feed, pager.start, pager.limit),
                               'pager': pager
                              },
                              context_instance=RequestContext(request))

##
# Renders the account settings page.
def account_settings_render(request):
    return render_to_response('account-settings.html',
                              {'account_page': True,
                              },
                              context_instance=RequestContext(request))


def _get_folder(request, folder_id):
    if not request.is_logged_in:
        user_id = settings.DEFAULT_USER_ID
    else:
        user_id = request.user_account.id
    try:
        if folder_id:
            folder = folder_models.Folder.objects.get(id=folder_id)
        else:
            folder = folder_models.Folder.objects.get(user=user_id, default_folder=True)
    except folder_models.Folder.DoesNotExist:
        if not request.is_logged_in:
            from future import Future
            from folders.utils import update_default
            Future(update_default)
            raise Http404
        else:#todo: clean up this temp fix for new users
            folder = folder_models.Folder.objects.get(user=settings.DEFAULT_USER_ID, default_folder=True)
    return folder


def nr_sort(raw_items, user):
    """
    Uses the Bayesian classifiers of the user to sort the list of raw
    items by guessed interestingness.
    """
    pass
