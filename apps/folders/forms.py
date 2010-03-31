from django import forms
from folders.constants import ITEMS_PER_PAGE_OPTIONS, DAY_LIMIT_OPTIONS

##
#    Folder edit form validator
class FolderEditForm(forms.Form):
    name = forms.CharField(max_length=30)
    items_per_page = forms.ChoiceField(choices=ITEMS_PER_PAGE_OPTIONS)
    days_old_limit = forms.ChoiceField(choices=DAY_LIMIT_OPTIONS, label='Show me highest ranked items from the last')
    raw_feed_id = forms.IntegerField(widget=forms.HiddenInput)

##
#    Folder add form validator
class FolderAddForm(forms.Form):
    name = forms.CharField(max_length=30)

class FeedAddForm(forms.Form):
    url = forms.URLField(max_length=512)
