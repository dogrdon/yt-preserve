import pafy
import yt_connect as ytc
import config.creds as creds

_BASE = 'https://www.youtube.com/'
_VID_PATH = 'watch?v='
_PL_PATH = 'playlist?list='

def add_index(playlist_data):
	pl_count = 1
	for i in playlist_data['items']:
		i['add_order'] = pl_count
		pl_count += 1
	return playlist_data


def downloadSave(playlist):
	playlist_url = _BASE+_PL_PATH+playlist
	playlist_data = pafy.get_playlist(playlist_url)
	playlist_data_idxd = add_index(playlist_data)
	for i in playlist_data_idxd['items']:
		vid_id = i['playlist_meta']['encrypted_id']
		vid_url = _BASE+_VID_PATH+vid_id
		video = pafy.new(vid_url)
		best_dl = video.getbest(preftype="mp4")
		filepath = "./videos/%s/%s.%s" % (i['add_order'], vid_id, best_dl.extension)
		print "now downloading %s - %s to %s" % (i['add_order'], i['playlist_meta']['title'], filepath)






if __name__ == '__main__':
	downloadSave(creds.YOUTUBE_PL)