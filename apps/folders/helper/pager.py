
##
# This class helps with figuring out pagination. If another page is available, etc...
#
class Pager(object):
    def __init__(self, page_number=1, limit=10, total_count=0, page_url=""): 
        self.current_page = page_number       
        self.limit = limit
        self.start = (page_number - 1) * limit + 1
        self.end = self.start + limit -1 if total_count > limit else total_count
        self.count = total_count
        self._previous_page = None
        self._next_page = None
        self._previous_page_url = None
        self._next_page_url = None
        self._page_count = None
        self.page_url=page_url
        
    ##
    # Lazy loading the value of the next page
    def _get_next_page(self):
        if not self._next_page:
            if self.count > self.current_page * self.limit: 
                self._next_page = self.current_page + 1
            else: 
                self._next_page = self.current_page
        return self._next_page
    
    ##
    # Lazy loading the value of the previous page
    def _get_previous_page(self):
        if not self._previous_page:
            if self.current_page > 1 : 
                self._previous_page = self.current_page - 1
            else: 
                self._previous_page = self.current_page
        return self._previous_page
    
    ##
    # Lazy loading the value of the total page count
    def _get_page_count(self):
        if not self._page_count:
            self._page_count = self.count / limit
        return self._page_count
    
    next_page = property(_get_next_page, None, None)
    previous_page = property(_get_previous_page, None, None)
    page_count = property(_get_page_count, None, None)
    
    def __unicode__(self):
        return "start: %s, limit: %s, count: %s  " % (self.start, self.limit, self.count)