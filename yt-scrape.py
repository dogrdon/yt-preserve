from pymongo import MongoClient
import os, sys
from lxml import html
import cssselect
from pprint import pprint
import csv

YT_FILE = "./data/youtube_QP_Favs.html"
LINK_BASE = "http://youtube.com/watch?v="

def captureYtData(yt_file):
	with open(yt_file, 'rt') as doc:
		htmlstring = doc.read()

	tree = html.fromstring(htmlstring)
	lis = tree.xpath('//ol[@id="vpl-videos-list"]/li')
	data = []
	
	count = len(lis)
	for li in lis:
		vid = li.xpath('a/span/@data-video-ids')[0]
		duration = li.xpath('a/span[@class="video-time"]/text()')[0]
		link = LINK_BASE + vid
		details = li.xpath('div/span/a/text()')
		title = details[0]
		user = details[1]
		views = li.xpath('div/span[@class="vpl-videos-list-info-views"]/text()')[0].strip().split(' ')[0]
		add_order = count
		record = {"id":vid,
				  "duration":duration,
				  "link":link,
				  "title":title.encode('utf-8'),
				  "user":user.encode('utf-8'),
				  "views":views,
				  "add_order": add_order}
		data.append(record)
		count -= 1

	return data

def dataToMongo(data):
	c = MongoClient()
	coll = c.yt_preserve.videos
	for d in data:
		coll.update({'_id':d['id']}, d, True)


def dataToCSV(data):
	with open('./data/yt_preserve.csv', 'wt') as f:
		file_writer = csv.writer(f)
		header = ['id', 'rev_order', 'duration', 'url', 'title', 'user', 'views']
		file_writer.writerow(header)
		for d in data:
			row = [d['id'], d['add_order'], d['duration'], d['link'], d['title'], d['user'], d['views']]
			print row
			file_writer.writerow(row)

if __name__ == '__main__':
	data = captureYtData(YT_FILE)
	dataToMongo(data)
	dataToCSV(data)
