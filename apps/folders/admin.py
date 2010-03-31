from django.contrib import admin
from folders.models import *

admin.site.register(Folder)
admin.site.register(RawFeed)
admin.site.register(SubscriptionFeed)
admin.site.register(RawItem)
admin.site.register(SubscriptionItem)

