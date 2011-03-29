import unittest

# Create a file called test_settings.py with the follow defined
from test_settings import consumer_key, consumer_secret, user_token, user_secret

class AuthTests(unittest.TestCase):

    def setUp(self):
        from micard.auth import OAuthHandler
        self.auth = OAuthHandler(consumer_key, consumer_secret)

    def test_request_token(self):
        self.auth._get_request_token()
    
    def test_get_auth_url(self):
        self.auth.get_authorization_url(register=False)
        self.auth.get_authorization_url(register=True)

class APITests(unittest.TestCase):

    def setUp(self):
        from micard.api import API
        from micard.auth import OAuthHandler
        
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(user_token, user_secret)
        
        self.api = API(auth)
    
    def test_questions(self):
        questions = self.api.get_questions()

    def test_me(self):
        me = self.api.me()
        self.assertTrue(me['email'])
        self.assertTrue(me['micard_id'])
    
    def test_history(self):
        history = self.api.history()
    
    def test_create_simple_history(self):
        from micard.error import MicardError
        questions = self.api.get_questions()
        
        responses = []
        for question in questions:
            [responses.append(x['id']) for x in question['responses']]
        
        responses.extend((100419000, 66986005))
        history = self.api.create_simple_history(condition=responses)
        self.assertEqual(len(history), len(responses))
        
    def test_create_medical_history(self):
        from micard.error import MicardError
        
        # Get some questionnaire questions+responses
        questions = self.api.get_questions()
        kwargs = {}
        total_responses = 0
        for question in questions:
            responses = []
            form_name = question['form_name']
            
            for response in question['responses']:
                responses.append(response['id'])
            
            try:
                kwargs[form_name].extend(responses)
            except:
                kwargs[form_name] = responses
            total_responses += len(responses)
        kwargs['bogus'] = 'valueasdf;lj'
        
        # Create a medical history based on the above
        history = self.api.create_medical_history(**kwargs)
        
        # this will fail because a medical history already exists.
        self.assertRaises(MicardError, self.api.create_medical_history, kwargs)
        
        self.assertEqual(len(history), total_responses)
    
    def test_supplement_registration(self):
        from micard.api import API
        from micard.error import MicardError
        from micard.auth import OAuthHandler
        import datetime
        
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.get_authorization_url()
        token = auth.request_token.key
        
        api = API(auth)
        
        supp = api.create_registration_supplement(
            consumer_key=consumer_key,
            token=token,
            email='address@domain.tld',
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
            emergency_number=5555551235,
            emergency_number_alt=5555551236,
            physician_name='Dr. First Last',
            physician_number=5555551237,
            power_of_attorney='First Last, J.D.',
            power_of_attorney_number=5555551238
        )
        
        # This will fail because the token above has already been supplemented
        self.assertRaises(MicardError, api.create_registration_supplement, {
            'consumer_key':consumer_key,
            'token': token,
        })
        
        api.delete_registration_supplement(
            consumer_key=consumer_key,
            token=token
        )
        

if __name__ == '__main__':
    unittest.main()

