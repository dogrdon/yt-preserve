'''see: http://stackoverflow.com/questions/21228815/adding-youtube-video-to-playlist-using-python'''
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
from oauth2client.tools import argparser, run_flow
import argparse, sys, os
import httplib2

YT_CLIENT_SECRET = 'config/client_secret.json'
YT_SCOPE = 'https://www.googleapis.com/auth/youtube'
YT_API_SERVICE_NAME = 'youtube'
YT_API_VERSION = 'v3'

def ytConnect():
	flow = flow_from_clientsecrets(YT_CLIENT_SECRET, scope=YT_SCOPE)
	store = Storage('config/%s-oauth2.json' % sys.argv[0])
	parser = argparse.ArgumentParser(parents=[tools.argparser])
	flags = parser.parse_args()
	credentials = run_flow(flow, store, flags)
	return build(YT_API_SERVICE_NAME, YT_API_VERSION, http=credentials.authorize(httplib2.Http()))
