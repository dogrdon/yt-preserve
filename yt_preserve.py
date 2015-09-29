import pafy
import yt_connect as ytc
import config.creds as creds
import json
import os, sys, errno
import hashlib
from pprint import pprint

_BASE = 'https://www.youtube.com/'
_VID_PATH = 'watch?v='
_PL_PATH = 'playlist?list='
_STORE_PATH = './videos'
_LAST_SAVE_FILE = './videos/last.json'

def add_index(playlist_data):
	pl_count = 1
	for i in playlist_data['items']:
		i['add_order'] = pl_count
		pl_count += 1
	return playlist_data

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python > 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def getPlaylistData(playlist=creds.YOUTUBE_PL):
	playlist_url = _BASE+_PL_PATH+playlist
	playlist_data = pafy.get_playlist(playlist_url)
	return add_index(playlist_data)

def getDirData(path=_STORE_PATH):
	'''returns a dictionary of information about the current directory storing the downloaded videos'''
	res = []
	dirData = {}

	for r,d,f in os.walk(path):
		res.append(d)

	ids = [i[0] for i in res[1:] if len(i) is not 0]
	
	for x in ids:
		dirData[int(res[0][ids.index(x)])] = x

	dirDataSorted = {}

	for key in sorted(dirData.iterkeys()):
		dirDataSorted[key] = dirData[key]

	return dirDataSorted

def fetchOldData():
	with open(_LAST_SAVE_FILE, 'rb') as fp:
		data = json.load(fp)
	return data

def repairMissing(dir_data, playlist_data):
	playlist_data_updated = {'playlist_id': playlist_data['playlist_id'], 
							 'description': playlist_data['description'], 
							 'title': playlist_data['title'], 
							 'items':[]}

	items = playlist_data_updated['items']
	olddata = fetchOldData()
	olditems = olddata['items']
	old_ids = [i['playlist_meta']['encrypted_id'] for i in olditems]
	new_ids = [i['playlist_meta']['encrypted_id'] for i in items]
	dir_ids = dir_data.values()

	'''PROBLEM: this is not adding the videos that have not been downloaded...and it doesn't know that there are any missing.'''
	'''SOLUTION: open last.json, which is a full record of what was saved last time, 
					- if dir data not in playlist data, but in old data something was deleted
					- if playlist data not in dir data and not in old data, it's new, add it.'''
	for x in playlist_data['items']:
		curr = x['playlist_meta']['encrypted_id']
		if curr in dir_ids:
			items.append(x)

		elif curr not in dir_ids and curr not in old_ids:
			items.append(x)

		else: '''TODO: this is not working, figure out why.'''
			for d in dir_ids:	
				if d not in new_ids and d in old_ids:
					print "adding removed: "
					items.append({'removed':'1', 'playlist_meta': {'encrypted_id': dir_data[int(x['add_order'])]}})

	return add_index(playlist_data_updated)

def dlVideos(playlist_data, modified=False):
	
	'''would want to skip this on subsequent passes 
			- you already have the data, you are working with a modified data package'''
	if modified == True:
		playlist_data_idxd = playlist_data
	else:
		playlist_data_idxd = getPlaylistData()

	existing_dirs = [x[1] for x in os.walk(_STORE_PATH)][0]

	playlist_data_len = int(len(playlist_data['items']))
	existing_dirs_len = int(len(existing_dirs))
	diff = playlist_data_len - existing_dirs_len

	if diff < 0:
		print "Looks like there are %s vidoes in the playlist" % (diff)
		'''figure out the gaps (which ids are present, which arent), make fixes to data passed around(add dummy entry to data), send back through?'''
		dirData = getDirData()

		playlist_data_idxd = repairMissing(dirData, playlist_data_idxd)

		print pprint(playlist_data_idxd)

		#getVideos(playlist_data_idxd, modified=True)
	else:
		for i in playlist_data_idxd['items']:
			vid_id = i['playlist_meta']['encrypted_id']
			vid_url = _BASE+_VID_PATH+vid_id
			order_id = i['add_order']
			dirname = vid_id
			filepath = "%s/%s/%s" % (_STORE_PATH, order_id, dirname)
			title = i['playlist_meta']['title']
			if str(order_id) not in existing_dirs:
					#TODO - factor gdata in
					video = pafy.new(vid_url, gdata=True)
					best_dl = video.getbest(preftype="mp4")
					ext = best_dl.extension
					mkdir_p(filepath)
					print "now downloading %s - %s to %s" % (order_id, title, filepath)
					best_dl.download(filepath=filepath)
					print "creating md5 hash..."
					vidname = [e for e in os.listdir(filepath) if e.endswith(ext)]
					videofile = filepath + '/' + vidname[0]
					h = hashlib.md5(open(videofile).read()).hexdigest()
					i['playlist_meta']['md5'] = h
					metadata = json.dumps(i['playlist_meta'], indent=4)
					metadata_file = './videos/%s/%s.json' % (order_id, vid_id)
					j = open(metadata_file, 'wt')
					print "depositing metadata for %s" % (title)
					j.write(metadata)
				

def refresh():
	#TODO HERE: 
			#           1) index the existing set of videos and hash it, make another index and check to see if it's different
			#			   - could be because something was added, or something was taken away
			#			2) in future downloads, check whats different and download only what's not already there.
	pass



if __name__ == '__main__':
	print "you have started the preserver..."
	data = getPlaylistData()
	dlVideos(data)