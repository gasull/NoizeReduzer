##
#    Logs in the given user
def login_user(request, user):
    request.session['user_id'] = user.id
    request.session['is_logged_in'] = True
    request.is_logged_in = True

##
#    Logs out the current user
def logout_user(request):
    if request.session.has_key('user_id'):
        del request.session['user_id']
    request.session['is_logged_in'] = False
    request.is_logged_in = False



