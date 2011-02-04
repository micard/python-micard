# Python-micard

Python-micard is simple API wrapper for micard.com that has 100% coverage.

## Installation

Using pip, you can install python-micard like so:

	pip install -e git+git://github.com/micard/python-micard.git#egg=micard
	
## Usage

### Authorization

**Step 1**:

Obtain a request token and store it somewhere safe. Then, redirect the user to the sign in url.

Here's an example of how you might accomplish this if you were writing a django view:

	def micard_login(request):
		from micard import OAuthHandler
	
		auth = micard.OAuthHandler('my_consumer_token', 'my_consumer_secret')
		signin_url = auth.get_authorization_url()
	    request.session['request_token'] = (
											auth.request_token.key, 
											auth.request_token.secret
											)
		return HttpResponseRedirect(signin_url)

**Step 2**:

After the user authorizes the request token, they will be redirected back to
your registered callback URL. Three pieces of information will be provided via
GET: oauth_verifier, oauth_token, and oauth_callback_confirmed.

Use this data to exchange your request token for an authorization token.

Here's an example using a django view:

	def micard_return(request):
		from micard import OAuthHandler
		
		request_token = request.session.get('request_token', None)
		token_key = request.GET.get('oauth_token', None)
		oauth_verifier = request.GET.get('oauth_verifier', None)

		if not request_token:
			logging.error("No OAuth token was found in the session data.")
			return HttpResponseRedirect(reverse('index'))
		else:
			del request.session['request_token']

		if request_token[0] != token_key:
			logging.error("Session token / miCARD returned token mismatch. \
						   request-token: %s; returned-token: %s" %
						   (request_token[0], returned_token)
						  )
			return HttpResponseRedirect(reverse('index'))

		if not oauth_verifier:
			logging.error("No oauth_verifier was provided by the SP. Failing")
			return HttpResponseRedirect(reverse('index'))

		auth = micard.OAuthHandler(getattr(settings, 'MICARD_CONSUMER_KEY'),\
			getattr(settings, 'MICARD_CONSUMER_SECRET'))

		auth.set_request_token(request_token[0], request_token[1])
		auth.get_access_token(oauth_verifier)

		request.session['user_token'] = auth.access_token.key
		request.session['user_secret'] = auth.access_token.secret

		return HttpResponseRedirect(reverse('some_place_cool'))

### Methods

Once you have an access token and secret, you can use all of the python-micard API methods like so:

	from micard import API, OAuthHandler
	
	auth = micard.OAuthHandler('my_consumer_token', 'my_consumer_secret')
	auth.set_access_token('user token', 'user secret')
	
	api = API(auth)
	
	print api.me
	print api.history()
	
	# Create a medical history by answering yes to every question on the 
	# miCARD medical questionnaire
	
	questions = self.api.get_questions()
	for question in questions:
		responses = []
		form_name = question['form_name']
		
		for response in question['responses']:
			responses.append(response['id'])
		
		try:
			kwargs[form_name].extend(responses)
		except:
			kwargs[form_name] = responses
	history = self.api.create_medical_history(**kwargs)

See [api.py](https://github.com/thomasw/python-micard/blob/master/micard/api.py) for a full list of available methods.

## Everything else

&copy; 2011 [miCARD LLC](https://micard.com/). See [LICENSE](https://github.com/thomasw/python-micard/blob/master/LICENSE) for details.

Substantial portions of this software are based on [Tweepy](https://github.com/joshthecoder/tweepy), an open source API wrapper for Twitter. Copyright and permission notices from Tweepy are located where applicable.