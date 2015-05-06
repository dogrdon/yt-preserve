import pafy
import yt_connect as ytc
import config.creds as creds
import json
import os, errno
import hashlib

_BASE = 'https://www.youtube.com/'
_VID_PATH = 'watch?v='
_PL_PATH = 'playlist?list='

def add_index(playlist_data):
	pl_count = 1
	for i in playlist_data['items']:
		i['add_order'] = pl_count
		pl_count += 1
	return playlist_data

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def firstDownloadSave(playlist):
	playlist_url = _BASE+_PL_PATH+playlist
	playlist_data = pafy.get_playlist(playlist_url)
	playlist_data_idxd = add_index(playlist_data)
	existing_dirs = [x[1] for x in os.walk('./videos')][0]
	for i in playlist_data_idxd['items']:
		vid_id = i['playlist_meta']['encrypted_id']
		vid_url = _BASE+_VID_PATH+vid_id
		video = pafy.new(vid_url)
		order_id = i['add_order']
		dirname = vid_id
		filepath = "./videos/%s/%s" % (order_id, dirname)
		title = i['playlist_meta']['title']
		if str(order_id) not in existing_dirs:
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
	firstDownloadSave(creds.YOUTUBE_PL)