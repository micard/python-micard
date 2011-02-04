import logging
import random

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

import micard

def login(request, register=None):
    auth = micard.OAuthHandler(getattr(settings, 'MICARD_CONSUMER_KEY'),\
        getattr(settings, 'MICARD_CONSUMER_SECRET'))
    
    # If register == true, the user will be presented with a signup page rather
    # than a login form.
    if register == True:
        signin_url = auth.get_authorization_url(register=True)
        api = micard.API(auth)
        api.create_registration_supplement(
            consumer_key=getattr(settings, 'MICARD_CONSUMER_KEY'),
            token=auth.request_token.key,
            email='address%s@domain.tld' % random.randint(0, 9999999999),
            first_name='first',
            last_name='last',
            phone=5555551234,
            address='101 Street St.',
            city='Orlando',
            state='Fl',
            zip_code=32817,
            gender='m',
            dob='15 July, 1984',
            emergency_name='first last sr.',
            emergency_number="5555551235",
            emergency_number_alt=5555551236,
            physician_name='Dr. First Last',
            physician_number=5555551237,
            power_of_attorney='First Last, J.D.',
            power_of_attorney_number=5555551238
        )
    else:
        signin_url = auth.get_authorization_url()
    
    # Store the token in their session for use when they return
    request.session['request_token'] = (auth.request_token.key, auth.request_token.secret)
    
    # Redirect them to miCARD for authorization
    return HttpResponseRedirect(signin_url)
    
def micard_return(request):
    request_token = request.session.get('request_token', None)
    token_key = request.GET.get('oauth_token', None)
    oauth_verifier = request.GET.get('oauth_verifier', None)
    
    # Check to make sure that the token we stored in the session is still there
    if not request_token:
        logging.error("No OAuth token was found in the session data.")
        return HttpResponseRedirect(reverse('index'))
    else:
        del request.session['request_token']
        
    # If the token from session and token from micard don't match, that
    # means something bad happened
    if request_token[0] != token_key:
        logging.error("Session token / miCARD returned token mismatch. request-token: %s; returned-token: %s" % (request_token[0], returned_token))
        return HttpResponseRedirect(reverse('index'))
    
    # We can't proceed without a verifier!
    if not oauth_verifier:
        logging.error("No oauth_verifier was provided by the SP. Failing")
        return HttpResponseRedirect(reverse('index'))
    
    # Exchange the temporary token/secret for a real token/secret
    auth = micard.OAuthHandler(getattr(settings, 'MICARD_CONSUMER_KEY'),\
        getattr(settings, 'MICARD_CONSUMER_SECRET'))
    
    auth.set_request_token(request_token[0], request_token[1])
    auth.get_access_token(oauth_verifier)
    
    request.session['user_token'] = auth.access_token.key
    request.session['user_secret'] = auth.access_token.secret
    
    # Redirect the user to the questionnaire so we can use the API to do stuff.
    return HttpResponseRedirect(reverse('questionnaire'))
    
def questionnaire(request):
    user_token = request.session.get('user_token', None)
    user_secret = request.session.get('user_secret', None)
    
    # No token/secret in the session.
    if not user_token or not user_secret:
        return HttpResponseRedirect(reverse('index'))
        
    auth = micard.OAuthHandler(getattr(settings, 'MICARD_CONSUMER_KEY'),\
        getattr(settings, 'MICARD_CONSUMER_SECRET'))
    auth.set_access_token(user_token, user_secret)
    api = micard.API(auth)
    
    # There is questionnaire form code in questionnaire.html. If this were
    # a real site, you shouldn't do it like this. Instead, create a form
    # class that is built dynamically based on the response to api.get_questions()
    # and you'd validate the POST response appropriately.
    #
    # Seriously. Don't do it like this.
    pay_prompt = False
    history = None
    if request.POST:
        history = api.create_medical_history(**request.POST)
        pay_prompt = True
    
    
    user_info = api.me()
    questions = api.get_questions()
    
    return render_to_response('questionnaire.html',{'user':user_info,
                                                    'questions': questions,
                                                    'pay_prompt': pay_prompt,
                                                    'history':history,
                                                    },context_instance=RequestContext(request))