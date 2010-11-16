from folders.models import Folder
from django_cron.base import cronScheduler, Job
from folders.utils import add_feed

#DOC: http://code.google.com/p/django-cron/wiki/Install
class UpdateDefaultFolder(Job):
    """
    Cron job that updates the default folder RSS feeds.
    """
    run_every = 900 # every 900 seconds = 15 min

    def job(self):
        update_default()

cronScheduler.register(UpdateDefaultFolder)

def update_default():
    """
    Updates/creates the default Folder, getting the info from
    http://www.bloglines.com/topblogs and removing Bloglines News from it.
    Should be run as a cron job, maybe w/django-cron.
    """
    default_folder = Folder.objects.get(id=1)
    # Gets list of most popular RSS feeds.  In the future we might decide to get
    # the list from somewhere else.
    rss_list = most_pop_bloglines()
    return [add_feed(default_folder, feed) for feed in rss_list]

def most_pop_bloglines():
    """
    Hardcoded b/c it needs human intervention for now.  Sometimes the Bloglines blog is
    among the most popular feeds in Bloglines.  Also, the feeds' links are not
    available in the page http://beta.bloglines.com/topfeeds
    """
    #TODO: Cron job that checks that the list keeps being the same
    result = [
        'http://feedproxy.google.com/DilbertDailyStrip',
        'http://rss.slashdot.org/Slashdot/slashdot',
        'http://rssfeeds.usatoday.com/UsatodaycomBooks-TopStories',
        'http://www.designspongeonline.com/feed',
        'http://www.nytimes.com/services/xml/rss/nyt/Books.xml',
        'http://www.engadget.com/rss.xml',
        'http://feeds.feedburner.com/drawn',
        'http://newsrss.bbc.co.uk/rss/newsonline_world_edition/front_page/rss.xml',
        'http://api.flickr.com/services/feeds/groups_pool.gne?id\x3d61057342@N00\x26lang\x3den-us\x26format\x3datom',
        'http://feeds.boingboing.net/boingboing/iBag',
    ]
    return result

