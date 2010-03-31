from django.contrib import admin
from django.conf.urls.defaults import *
from folders.views import *
from users.views import *
import os.path

#===============================================================================
# Initializing Django url patterns.  This is done once with application load
#===============================================================================
admin.autodiscover()

import django_cron
django_cron.autodiscover()

urlpatterns = patterns('',
    url(r"^register.html$", registration, name="user_registration"),
    url(r"^folder-(\d{1,10})-edit\.html$", folder_edit, name="folder_edit"),
    # "render_folder" b/c the main purpose is rendering, although editing is possible.
    url(r"^folder-(?P<folder_id>\d{1,10})-p(?P<page>\d{1,2})-(.*)\.html$", folder_render, name="folder_render_pagination"),
    url(r"^folder-(?P<folder_id>\d{1,10})-(.*)\.html$", folder_render, { 'page': 1 }, name="folder_render"),
    url(r"^account-settings\.html$", account_settings_render, name="account_settings"),
    url(r"^login\.html$", login, name="login"),
    url(r"^logout\.html$", login, { 'logout_requested': True }, "logout"),
    url(r"^$", folder_render, name="home"),
    url(r'^folder-(?P<folder_id>\d{1,10})/feed-(?P<subscription_feed_id>\d{1,10})-(.*)\.html$',
        feed_render,
        { 'page': 1 },
        name="feed_render"),
    url(r'^folder-(?P<folder_id>\d{1,10})/feed-(?P<subscription_feed_id>\d{1,10})-p(?P<page>\d{1,2})-(.*)\.html$',
        feed_render,
        { 'page': 1 },
        name="feed_render_pagination"),
    (r"^admin/(.*)", admin.site.root),
)

# b/c http://docs.djangoproject.com/en/dev/howto/static-files/#limiting-use-to-debug-true
from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^css/(?P<path>.*)$",
            "django.views.static.serve",
            {'document_root': settings.MEDIA_ROOT + 'static/css/' },
            name="css"),
        url(r"^js/(?P<path>.*)$",
            "django.views.static.serve",
            {'document_root': settings.MEDIA_ROOT + 'static/js/' },
            name="js"),
        url(r"^images/(?P<path>.*)$",
            "django.views.static.serve",
            {'document_root': settings.MEDIA_ROOT + 'static/images/' },
            name="images"),
        url(r"^tests/(?P<path>.*)$",
            "django.views.static.serve",
            {'document_root': os.path.join(os.path.dirname(__file__), 'templates/tests').replace('\\','/')}, 
            name="tests"),
    )

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
