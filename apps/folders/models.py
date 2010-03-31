import calendar
import time
from datetime import timedelta, datetime

from django.conf import settings
from django.db import models

from folders.constants import ITEMS_PER_PAGE_OPTIONS, DAY_LIMIT_OPTIONS
from users.models import UserAccount

class Folder(models.Model):

    def __init__(self, *args, **kwargs):
        self._feeds = None
        self._items = None
        self.start = 1
        self._item_count = None
        models.Model.__init__(self, *args, **kwargs)

    user = models.ForeignKey(UserAccount,
                             null=True,
                             verbose_name='user of the folder')
    default_folder = models.BooleanField('is it the default folder for its user?',
                                         default=True)
    name = models.CharField('name of the folder',
                            max_length=30)

    # What if someone subscribes to, say, a hardcore gay porn RSS feed?
    # Will they want the shared option to be enabled by default?  Let's
    # be privacy-friendly.
    shared = models.BooleanField('is it shared?',
                                 default=False)
    items_per_page = models.IntegerField('number of items per page',
                                         default=25, choices=ITEMS_PER_PAGE_OPTIONS)
    days_old_limit = models.IntegerField('number of days RSS items are kept',
                                         default=14, choices=DAY_LIMIT_OPTIONS)
    # If specified, item rank will only be based off this list of criteria
    rank_criteria = None

    ##
    # Lazily retrieves the feeds associated to the folder
    def get_feeds(self):
        if not self._feeds:
            self._feeds = SubscriptionFeed.objects.filter(folder=self.id)
        return self._feeds
    
    def get_item_count(self):
        if not self._item_count:
            self._item_count = SubscriptionItem.objects.filter(feed__in=self.feeds).select_related(depth=1).count()
        return self._item_count

    feeds = property(get_feeds, None, None)
    item_count = property(get_item_count, None, None)

    ##
    # For the future undo button
    def unmark_clicked(item):
        item.clicked = False
        item.save()

    def __unicode__(self):
        return "folder name: " + self.name


class RawFeed(models.Model):
    
    def __init__(self, *args, **kwargs):
        self._items = None
        models.Model.__init__(self, *args, **kwargs)
        
    link = models.URLField('URL of the RSS feed',
                           max_length=512,
                           unique=True)
    default_name = models.CharField('name of the feed or blog',
                                    max_length=512)
    description = models.CharField('description of the feed',
                                   max_length=4096,
                                   blank=True,
                                   null=True)
    favicon = models.ImageField('Favicon of the website feed',
                                upload_to='data/favicons/',
                                null=True)
    
    def _get_items(self):
        if not self._items:
            self._items = RawItem.objects.filter(raw_feed=self.id)
        return self._items
    
    items = property(_get_items) 

    def __unicode__(self):
        return self.default_name + "(" + self.link + ")"
    class Meta:
        ordering = ["default_name"]

class SubscriptionFeed(models.Model):
    def __init__(self, *args, **kwargs):
        self._items = None
        self._name = None
        self._item_count = None
        models.Model.__init__(self, *args, **kwargs)

    custom_name = models.CharField('name given by the user of the feed',
                            max_length=512,
                            null=True,
                            blank=False)
    date_added = models.DateField('date the feed was added by the user',
                                  auto_now=True)

    # the attributes of a RSS feed
    rawfeed = models.ForeignKey(RawFeed,
                                verbose_name='RSS feed this feed subscription belongs to')

    # the folders it belongs to.  Users might want to have the same RSS feed in
    # more than one folder, even if it is nonsense.
    folder = models.ForeignKey(Folder,
                               verbose_name='User folder this feed subscription belongs to')

    def _get_items(self):
        if not self._items:
            date_limit = datetime.utcnow() - timedelta(days=self.folder.days_old_limit)
            self._items = SubscriptionItem.objects.filter(feed=self.id,
                                              raw_item__published_date__gt = date_limit).order_by('-raw_item__published_date').select_related(depth=2)[:self.folder.items_per_page]
        return self._items
    
    def get_item_count(self):
        if not self._item_count:
            self._item_count = SubscriptionItem.objects.filter(feed=self).select_related(depth=1).count()
        return self._item_count
    
    def _get_name(self):
        if not self._name:
            self._name = self.custom_name or self.rawfeed.default_name
        return self._name
    
    def _set_name(self, name):
        if name and name != '' and name != self.name:
            self.custom_name, self._name = name, name

    items = property(_get_items)    
    name = property(_get_name, _set_name)
    item_count = property(get_item_count)

    def __unicode__(self):
        return self.name + '(RawFeed: ' + self.rawfeed.__unicode__() + ')'
    class Meta:
        ordering = ['custom_name']

class RanksItem(models.Model):
    #TODO: Troubleshoot for items w/o URL
    link = models.URLField('URL of the RSS item', max_length=512)
    delicious = models.IntegerField('Number of bookmarks in delicious.com', default=0)
    digg = models.IntegerField('Number of diggs', default=0)
    reddit = models.IntegerField('Votes in reddit.com', default=0)

class RawItem(models.Model):

    def __init__(self, *args, **kwargs):
        self._feeds = None
        self._items = None
        self._local_published_date = None
        models.Model.__init__(self, *args, **kwargs)

    title = models.CharField('Title of the RSS item',
                             max_length=512,
                             blank=True,
                             null=True)
    body = models.TextField('Body/description of the RSS item',
                            max_length=4096,
                            blank=True,
                            null=True)
    published_date = models.DateTimeField('Date when the RSS item was published', default=datetime.now())
    rank = models.ForeignKey(RanksItem,
                             verbose_name='Rank of the link in several social websites')
    raw_feed = models.ForeignKey(RawFeed,
                                 verbose_name='RawFeed the RawItem belongs to')

    ##
    # Returns the published date converted to local time
    def get_local_published_date(self):
        if not self._local_published_date:
            secs = calendar.timegm(self.published_date.utctimetuple())
            self._local_published_date = datetime.fromtimestamp(time.mktime(time.localtime(secs)))
        return self._local_published_date

    local_published_date = property(get_local_published_date, None, None)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["rank"]
        unique_together = (("rank", "raw_feed"),)

class SubscriptionItem(models.Model):
    read = models.BooleanField('Has the user read the item?', default=False)
    clicked = models.BooleanField('Has the user clicked on the link?',
                                  default=False)
    already_in_rss = models.BooleanField('Is it already in the folder RSS?', default=False)
    # the attributes of a RSS item: title, link, body, etc.
    raw_item = models.ForeignKey(RawItem,
                                verbose_name='RSS raw item attributes of this RSS subscription item')
    feed = models.ForeignKey(SubscriptionFeed,
                             verbose_name='RSS feed of this subscription item')

    #XXX: This should be renamed/refactored or removed.  Is it going to be a recomendation engine
    # based in users with similar tastes?
    interesting = models.BooleanField('Does the bayesian filter finds this interesting for the user?',
                                      default=False)

    will_be_read = models.BooleanField(
        'Bayesian classifier that guesses if the user will read it')
    will_be_clicked = models.FileField(
        'Bayesian classifiear that guesses if the user will click the link',
        upload_to=settings.CLASSIFIERS_DIR)

    def mark_read(item):
        "Mark an RSS item as read"
        item.read = True
        item.save()

    def unmark_read(item):
        item.read = False
        item.save()

    def mark_clicked(item):
        item.clicked = True
        item.save()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
