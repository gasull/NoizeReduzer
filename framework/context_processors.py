from settings import jquery_path, yui_css_path
##
# Returns context variables to be used for media paths.
# See http://docs.djangoproject.com/en/dev/ref/templates/api/#id1
# for more info on this. -Aaron
def media_paths(request):

    return {
        "jspath": "/static/js/",
        "csspath": "/static/css/",
        "imagespath": "/static/images/",
        "jquery_path": jquery_path,
        "yui_css_path": yui_css_path
        }
