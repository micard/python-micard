from django.conf.urls.defaults import *

urlpatterns = patterns('micard_auth.views',
    # Authorization related
    url(r'^register/$', 'login', name='register', kwargs={'register':True}),
    url(r'^login/$', 'login', name='login'),
    url(r'^return/$', 'micard_return', name='micard_return'),
    # Do stuff with the API once the user is authorized.
    url(r'^questionnaire/$', 'questionnaire', name='questionnaire')
)