from urlparse import urljoin
from auth import OAuthHandler

from methods import method_factory

class API(object):
    def __init__(self, auth, host='https://micard.com', api_root='/api/1'):
        self.auth = auth
        self.host = host
        self.api_root = api_root
        self.url = urljoin(host, api_root)
        
    get_questions = method_factory(
        path = '/questions.json',
        allowed_param=[]
    )
    
    me = method_factory(
        path = '/me.json',
        allowed_param=[],
        require_auth = True
    )
    
    history = method_factory(
        path = '/me/history.json',
        allowed_param = [],
        require_auth = True
    )
    
    create_medical_history = method_factory(
        path = '/me/history.json',
        method = 'POST',
        require_auth = True
    )
    
    create_registration_supplement = method_factory(
        path = '/supplement_registration.json',
        method = 'POST',
        require_auth = True
    )
    
    delete_registration_supplement = method_factory(
        path = '/supplement_registration.json',
        method = 'DELETE',
        require_auth = True
    )