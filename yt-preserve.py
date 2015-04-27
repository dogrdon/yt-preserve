import pafy
from pymongo import MongoClient

def updateRecords():
	c = MongoClient()
	coll = c.yt_preserve.videos
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

if __name__ == '__main__':
	updateRecords()