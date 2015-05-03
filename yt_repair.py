import pafy
from pymongo import MongoClient
import csv
import yt_connect as ytc

c = MongoClient()
coll = c.yt_preserve.videos

def updateRecords():
	data = coll.find()

	for d in data:
		url = d['link']
		title = d['title'].encode('utf-8')

		try:
			vid = pafy.new(url)
			update = {'available': 1,
					  'description': vid.description,
					  'keywords': vid.keywords,
					  'update_views': vid.viewcount,
					  'age_ver': vid.age_ver,
					  'uploaded': vid.published,
					  'new_rating': vid.rating,
					  'category': vid.category,
					  'curr_duration': vid.duration
					  }
			coll.update({'_id':d['id']}, {'$set':update})
		except IOError:
			update = {'available':0}
			coll.update({'_id':d['id']}, {'$set':update})
		except ValueError as e:
			print "There was an error: ", e
			continue

def getUnavailable():
	'''get the unavailable records for a little manual remediation'''
	unavailable = coll.find({"available":0})
	
	with open('./data/yt-unavailable.csv', 'wt') as f:
		file_writer = csv.writer(f)
		unavail_headers = ['id', 'add_order', 'duration', 'link', 'title', 'user', 'views']
		file_writer.writerow(unavail_headers)
		for i in unavailable:
			row = [i['id'], i['add_order'], i['duration'], i['link'], i['title'].encode('utf-8'), i['user'].encode('utf-8'), i['views']]
			file_writer.writerow(row)

def updateUnavailable():
	with open('./data/yt-unavailable_updated.csv', 'rU') as f:
		csvdata = csv.reader(f)
		header = next(csvdata)
		headerIdx = {header[i]: i for i in range(len(header))}

		for c in csvdata:
			newurl = c[headerIdx['viable_replacement']].strip()
			vidID = c[headerIdx['id']]
			video_disp = c[headerIdx['video_disposition']]
			user_disp = c[headerIdx['user_disposition']]
			if newurl != 'na':
				data = {
					"new_copy": newurl,
					"status": 'refreshed',
					"user_disposition": user_disp,
					"video_disposition": video_disp
					}
			else:
				data = {"status":"gone",
						"user_disposition": user_disp,
						"video_disposition": video_disp
						}

			coll.update({'_id':vidID}, {'$set':data})

def arrangeIDs():
	available = coll.find({"available":1})
	unavailable = coll.find({"available":0})

	for a in available:
		vidID = a['id'].strip()
		data = {'uploadID':vidID}
		coll.update({'_id':vidID}, {'$set':data})

	for u in unavailable:
		vidID = u['id'].strip()
		if 'new_copy' in u:
			uvidID = u['new_copy'].split('?v=')[1].strip()
		else:
			uvidID = 'VOID'
		data = {'uploadID':uvidID}
		coll.update({'_id':vidID}, {'$set':data})

def uploadToPlaylist(playlist):
	data = coll.find().sort('add_order', 1)
	youtube_client = ytc.ytConnect()
	playlistID = playlist
	for d in data:
		video_id = d['uploadID']
		if video_id != 'VOID':
			body = {'snippet':{
						'playlistId': playlistID,
						'resourceId': {
							'kind': 'youtube#video',
							'videoId': video_id
						}
				}
			}
			print 'uploading %s now ...' % (video_id)
			add_video_request = youtube_client.playlistItems().insert(part="snippet", body=body).execute()

def downloadFromPlaylist():
	pass

if __name__ == '__main__':
	#updateRecords()
	#getUnavailable()
	#updateUnavailable()
	#arrangeIDs()
	uploadToPlaylist()

