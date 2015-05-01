from oauth2client.client import OAuth2WebServerFlow
import .config.auth as creds
import httplib2

'''from https://developers.google.com/api-client-library/python/guide/aaa_oauth#acquiring'''

def ytConnect():
	flow = OAuth2WebServerFlow(client_id=creds.CLIENT_ID,
	                           client_secret=creds.CL_SECRET,
	                           scope='https://www.googleapis.com/auth/youtube',
	                           redirect_uri='http://example.com/auth_return')
	auth_uri = flow.step1_get_authorize_url()
	credentials = flow.step2_exchange(code) #what is code here?
	http = httplib2.Http()
	http = credentials.authorize(http)
