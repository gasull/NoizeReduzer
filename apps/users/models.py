from django.db import models
from django import forms
from settings import default_user_id

USER_TYPES = (
    (1, 'DEFAULT_USER'),
    (2, 'NOT_QUITE_USER'),
    (3, 'ANONYMOUS_USER'),
    (4, 'REGISTERED_USER'),
    (5, 'PREMIUM_USER'),
)

USER_STATUS = (
    (1, 'ACTIVE'),
    (2, 'DELETED'),
)

class UserAccount(models.Model):

    username = models.CharField(max_length=30, null=True)
    password = models.CharField(max_length=16, null=True)
    email = models.EmailField(null=True)
    type = models.IntegerField(max_length=1, choices=USER_TYPES) # represents user account type
    status = models.IntegerField(max_length=1, choices=USER_STATUS) # represents user account status
    on_announce_list = models.BooleanField(default=True)
    
    def check_if_default_user(self):
        return self.id == default_user_id
    
    is_default_user = property(check_if_default_user)

    def __unicode__(self):
        return 'user_id: ' + str(self.id)

##
#    This class is extra meta data on top of Django's Authentication System's
#    User class.  Please see chapter 12 of the Django book for details.  -Aaron
class UserProfile(models.Model):

    user = models.OneToOneField(UserAccount, unique=True)
    firstname = models.CharField(max_length=30, null=True)
    lastname = models.CharField(max_length=30, null=True)
    #makes more sense to have the displayname as a profile attribute than as a preference -Aaron
    displayname = models.CharField(max_length=30, null=True)
    location = models.CharField(max_length=30, null=True)
    gender =  models.CharField(max_length=1, null=True)
    date_of_birth = models.DateField(null=True)

    def __unicode__(self):
        return 'displayname: ' + self.displayname


class UserGuessers(models.Model):
    """
    Bayesian guessers for recommending RSS items to the user.
    Each guesser will be an Orange .tab file with these columns:
    - raw_feed.id
    - word_from_the_field (It's a word from the field used for this guesser)
    - guess (Boolean: either True or False)
    """
    user = models.OneToOneField(UserAccount, unique=True)
    #FIXME: Each user need to have his own file for each guesser.
    guess_read_from_link_text = models.FileField(
            'Bayesian classifier that guesses if the user will read it', 
            upload_to='data/bayes/guess_read_from_link_text/')
    guess_read_from_link_url = models.FileField(
            'Bayesian classifier that guesses if the user will read it', 
            upload_to='data/bayes/guess_read_from_link_url/')
    guess_click_from_link_text = models.FileField(
            'Bayesian classifier that guesses if the user will click it', 
            upload_to='data/bayes/guess_click_from_link_text/')
    guess_click_from_link_url = models.FileField(
            'Bayesian classifier that guesses if the user will click it', 
            upload_to='data/bayes/guess_click_from_link_url/')
    guess_click_from_content = models.FileField(
            'Bayesian classifiear that guesses if the user will click the link',
            upload_to='data/bayes/guess_click_from_content/')
    #TODO: Guesser based on what people with similar interests are 
    # reading/clicking
    

class Billing(models.Model):
    user = models.ForeignKey(UserAccount, unique=True)
    firstname = models.CharField(max_length=30, null=True)
    lastname = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    zipcode = models.CharField(max_length=28)

    def __unicode__(self):
        return 'address: %s city: %s state: %s zipcode: %s country: %s' % \
                (self.address, self.city, self.state, self.zipcode, \
                self.country)
    
##
#    User registration form validator 
class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput, max_length=30)
    password_verfication = forms.CharField(widget=forms.PasswordInput, max_length=30)   
    on_announce_list = forms.BooleanField(required=False)
    
    def is_valid(self):
        return forms.Form.is_valid(self) and \
                self.cleaned_data['password'] == self.cleaned_data['password_verfication']
  
##
#    User signin form validator   
class SignInForm(forms.Form):
    username = forms.CharField(max_length=30, label="Username/Email")
    password = forms.CharField(widget=forms.PasswordInput, max_length=30)
