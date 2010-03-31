from users.models import UserAccount

##
#    Supporting class for the LoginMiddleware.  Saves a DB per page load by 
#    lazy loading the logged in user account. -Aaron
class LazyUser(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user_account'):
            request._cached_user_account = self.get_user_account(request)
        return request._cached_user_account
    
    def get_user_account(self, request):
        if request.is_logged_in and request.session.has_key("user_id"):
            return UserAccount.objects.get(pk=int(request.session["user_id"]))
        return None
            
      
 ##
 #    Based off of "django.contrib.auth.middleware.AuthenticationMiddleware"
 #    This class provides easy access to the user account object of the logged
 #    in user.  Also guarantees that you can pull the logged in status off
 #    the request object at all times. -Aaron
class LoginMiddleware(object):
    
    def process_request(self, request):
        assert hasattr(request, 'session'), "The custom authentication middleware requires session middleware to be installed."
        request.__class__.user_account = LazyUser()
        if request.session.has_key("is_logged_in"):    
            request.is_logged_in = request.session["is_logged_in"] == True
        else:
            request.is_logged_in = False            
        return None