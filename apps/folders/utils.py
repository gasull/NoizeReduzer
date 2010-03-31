from folders.models import RawFeed, RawItem, SubscriptionFeed, SubscriptionItem, RanksItem, Folder
import feedparser
from datetime import timedelta
import datetime, time
from psycopg2 import DataError
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
import logging
import sys
import pdb

class CannotParseFeed(Exception):
    def __init__(self, url):
        logging.warning('Cannot parse the feed: ' + url)

##
# Adds the feed to the folder.
# @param folder folder where the feed will be added
# @param url link of the feed
def add_feed(folder, url):
    """
    >>> from folders.models import Folder
    >>> folder = Folder()
    >>> folder.save()
    >>> startdate = datetime.datetime.now()
    >>> dict = add_feed(folder, 'http://feeds.boingboing.net/boingboing/iBag')
    >>> rawfeed = dict['rawfeed']
    >>> rawfeed.link == 'http://feeds.boingboing.net/boingboing/iBag'
    True
    >>> rawfeed.default_name == 'Boing Boing'
    True
    >>> rawfeed.description == ''
    True
    >>> feed = dict['feed']
    >>> feed.name == 'Boing Boing'
    True
    >>> feed.folder is not None
    True
    >>> rawitems = dict['rawitems']
    >>> len(rawitems) > 0
    True
    >>> item = rawitems[0]
    >>> item.published_date > startdate
    True
    >>> items = dict['items']
    >>> len(items) > 0
    True
    >>> dict = add_feed(folder, 'http://feedproxy.google.com/DilbertDailyStrip')
    """
    logging.info('Adding feed %s' % url)
    parsed_data = feedparser.parse(url)
    if 'bozo_exception' in parsed_data.keys() and len(parsed_data.entries) == 0:
        # The URL wasn't accesed.
        #XXX: Throw exception and capture it in the view showing a message sayin that the feed is invalid.
        return
    # No bozo_exception, then the URL was accessed.
    feed, raw_items, items = None, None, None
    try:
        rawfeed, created = RawFeed.objects.get_or_create(
            link=url,
            defaults={
                'default_name': parsed_data.feed.title,
                'description': parsed_data.channel.description,
            })
        if created:
            logging.debug('Created RawFeed %s: %s' % (rawfeed.default_name,
                                                     rawfeed.link))
        else:
            logging.debug('Gotten RawFeed %s: %s' % (rawfeed.default_name, rawfeed.link))
    except MultipleObjectsReturned:
        _log_error(rawfeed)
        #TODO: Remove dup
    except DataError:
        _log_error(rawfeed)
    else:
        feed, raw_items, items, created = _save_feed(parsed_data, folder, url, rawfeed)
    return {'rawfeed': rawfeed,
            'feed': feed,
            'rawitems': raw_items,
            'items': items}

##
# Saves Feed
def _save_feed(parsed_data, folder, url, rawfeed):
    raw_items, items = None, None
    try:
        feed, created = SubscriptionFeed.objects.get_or_create(
            custom_name=None,
            rawfeed = rawfeed,
            folder = folder
            )
        if created:
            logging.debug('Created SubscriptionFeed %s.' % feed.name)
        else:
            logging.debug('Gotten SubscriptionFeed %s.' % feed.name)
    except MultipleObjectsReturned:
        _log_error(SubscriptionFeed())

        #TODO: Remove dup
    except DataError:
        _log_error(feed)
    else:
        raw_items, items = _save_ranksitems(parsed_data, folder, feed)
    return feed, raw_items, items, created

def _save_ranksitems(parsed_data, folder, feed):
    raw_items = []
    items = []
    for entry in parsed_data.entries:
        try:
            ranks_item, created = RanksItem.objects.get_or_create(link=entry.link)
            if created:
                logging.debug('Created RanksItem %s.' % entry.link)
            else:
                logging.debug('Gotten RanksItem %s.' % entry.link)
        except MultipleObjectsReturned:
            _log_error(RanksItem())
            #TODO: Remove dup
        except DataError:
            _log_error(ranks_item)
        except AttributeError:
            raise CannotParseFeed(feed.rawfeed.link)
        else:
            raw_items, items = _save_raw_item(entry, folder, feed, ranks_item,
                                              raw_items, items)
    return raw_items, items

def _save_raw_item(entry, folder, feed, ranks_item, raw_items, items):
    try: # RSS (AFAIK)
        body = entry.content[0].value
    except AttributeError:
        try: # Atom (AFAIK)
            body = entry.summary
        except AttributeError:
            body = ''
    try: # Does the entry have a date?
        updated_parsed = entry.updated_parsed
    except AttributeError:
        published_date = datetime.datetime.now()
    else:
        published_date = datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
    try:
        logging.debug("get_or_create: " + entry.link)
        raw_item, created = RawItem.objects.get_or_create(
            rank=ranks_item,
            raw_feed=feed.rawfeed,
            defaults={'title': entry.title,
                      'body': body,
                      'published_date': published_date,
                      'rank': ranks_item,
                      'raw_feed': feed.rawfeed,
                     })
        if created:
            logging.debug('Created RawItem: %s.' % raw_item)
        else:
            logging.debug('Gotten RawItem: %s.' % raw_item)
        logging.debug('RawItems in DB: %s' % RawItem.objects.count())
    except MultipleObjectsReturned:
        _log_error(RawItem())
        #TODO: Remove dup
    except DataError:
        # Maybe some field is too long.
        _log_error(raw_item)
    else:
        raw_items.append(raw_item)
        items = _save_item(folder, raw_item, feed, items)
    return raw_items, items

def _save_item(folder, raw_item, feed, items):
    item = SubscriptionItem()
    item.read = False
    item.clicked = False
    item.raw_item = raw_item
    item.feed = feed
    item.folder = folder
    try:
        item, created = SubscriptionItem.objects.get_or_create(
            raw_item=item.raw_item,
            defaults={'read': item.read,
                      'clicked': item.clicked,
                      'feed': item.feed,
                     })
        if not created:
            logging.debug("Item wasn't created: " + raw_item.__unicode__())
    except MultipleObjectsReturned:
        _log_error(SubscriptionItem())
        #TODO: Remove dup
    except DataError:
        _log_error(item)
    else:
        items.append(item)
    return items

def _log_error(model):
    exception  = sys.exc_info()[1]
    if exception.message[:42] == 'value too long for type character varying(':
        logging.error(exception)
        offending_length = int(exception.message[42:].split(')')[0])
        for key in model.__dict__.keys():
            try:
                length = len(model.__dict__[key])
            except:
                # Not a string field.
                pass
            else:
                if length < offending_length:
                    logging.error(model.__class__.__name__ + '.' + key
                                  + ' might be the offending attribute.')
    else:
        logging.error(exception.message)

#TODO: Schedule job that fetches the ranks periodically?

##
# Calculates the rank for a link.
# @param url link of the story
# @return integer with the rank
def rank(url):
    """
    >>> 0 <= rank('http://www.techcrunch.com/2009/01/18/why-google-employees-quit/')
    True
    >>> rank('')
    0
    >>> rank(None)
    0
    >>> rank('junk')
    0
    """
    # Bookmarking for own reference has more value than upvoting it
    # for other people in community news websites.  A story on Digg
    # usally has thousands of votes, but a link is rarely bookmarked
    # a thousand times.
    result = 0
    try:
        ranks = RanksItem.objects.get(link=url)
    except RanksItem.DoesNotExist:
        pass
    else:
        result = 10 * ranks.delicious + ranks.digg + ranks.reddit
    finally:
        return result

@transaction.commit_manually
def copy_folder(folder,user):
    feeds, items = [], []
    folderCopy = Folder(default_folder=True,
                        user=user,
                        name=folder.name)
    folderCopy.save()
    transaction.commit()
    for feed in folder.feeds:
        feedCopy = SubscriptionFeed(custom_name=None,
                                    rawfeed =feed.rawfeed,
                                    folder =folderCopy)
        feedCopy.save()
        feeds.append(feedCopy)
        
    transaction.commit()        
    for feed in feeds:
        for item in feed.rawfeed.items:
            itemCopy = SubscriptionItem(read = False,
                                         clicked = False,
                                         raw_item = item,
                                         feed = feed)
            itemCopy.save()
    transaction.commit()
    
    return folderCopy
            

def get_folder_feed_items(folder, start, limit):
    if not folder or not start or not limit:
        return None
    date_limit = datetime.datetime.now() - timedelta(days=folder.days_old_limit)
    items = SubscriptionItem.objects.filter(feed__in=folder.feeds,
                                              raw_item__published_date__gt = date_limit).order_by('-raw_item__published_date').select_related(depth=2)[start:start+limit]
    return items
                                              
                
def get_feed_items(feed, start, limit):
    if not feed or not start or not limit:
        return None
    date_limit = datetime.datetime.utcnow() - timedelta(days=feed.folder.days_old_limit)
    return SubscriptionItem.objects.filter(feed=feed.id,
                                              raw_item__published_date__gt = date_limit).order_by('-raw_item__published_date').select_related(depth=2)[start:limit]

