import os
import re
import glob
import sys
import praw
import requests
import BeautifulSoup
from random import randint

MIN_SCORE = 100
amount = 0
subreddits = []
imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')

error = """
		Error: You must input some arguments when running this script. The format of the commands are:
		Get x amount of random image links: bot.py -r [Positive Number > 0] [List of subreddit names separated by a space]
		Download x amount of random images: bot.py -d [Positive Number > 0] [List of subreddit names separated by a space]
		""" 

#Check if the user has inputted the right amount of arguments and if they did then store the valuable data
if len(sys.argv) <= 3:
	print error
	exit(0)
elif len(sys.argv) >3 and int(sys.argv[2]) > 0 and (sys.argv[1] == '-r' or sys.argv[1] == '-d'):
	amount = int(sys.argv[2])
	for x in range(3,len(sys.argv)):
		subreddits.append(sys.argv[x])
else:
	print error
	exit(0)

#function used to download the files to the same repository that bot.py is in
def downloadImage(imageUrl, localFileName):
	response = requests.get(imageUrl)
	
	if response.status_code == 200:
		print('Downloading %s ...' % (localFileName))
	
		with open(localFileName, 'wb') as fileObject:
			for chunk in response.iter_content(4096):
				fileObject.write(chunk)

bot = praw.Reddit(user_agent = "Grabbing random images and downloading x images from subreddits")

#go through each subreddit the user has specified and randomly choose a subset of the total number of images desired 
for sub in subreddits:
	random = randint(1, amount) if amount != 0 else 0
	amount = amount - random
	subreddit = bot.get_subreddit(sub)
	submissions = subreddit.get_hot(limit=25)
	
	#for the randomly selected subset of the total images needed, go through all the submissions and find a valid image link to spit out or download
	for x in range(0,random):
		for submission in submissions:
		    if "imgur.com/" not in submission.url:
		        continue
		    if submission.score < MIN_SCORE:
		        continue
		    if len(glob.glob('reddit_%s_*' % (submission.id))) > 0:
		        continue
			#This if body is to get images in an album
			if 'http://imgur.com/a/' in submission.url:
				if(sys.argv[1] == '-r'):
					print(submission.url)
		    		break
		    	else:
					albumId = submission.url[len('http://imgur.com/a/'):]
					htmlSource = requests.get(submission.url).text

					soup = BeautifulSoup(htmlSource)
					matches = soup.select('.album-view-image-link a')

					for match in matches:
						imageUrl = match['href']
						if '?' in imageUrl:
							imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
						else:
							imageFile = imageUrl[imageUrl.rfind('/') + 1:]
						localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (sub, submission.id, albumId, imageFile)
						downloadImage('http:' + match['href'], localFileName)
					break
			#This if body is to get direct images
		    elif 'http://i.imgur.com/' in submission.url:
		    	if(sys.argv[1] == '-r'):
					print(submission.url)
					break
		    	else:	
			        mo = imgurUrlPattern.search(submission.url)

			        imgurFilename = mo.group(2)
			        if '?' in imgurFilename:
			            imgurFilename = imgurFilename[:imgurFilename.find('?')]

			        localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (sub, submission.id, imgurFilename)
			        downloadImage(submission.url, localFileName)
			    	break
			#This if body is to get images that are not of the "i.imgur...." and album type
		    elif 'http://imgur.com/' in submission.url:
		        if(sys.argv[1] == '-r'):
		        	print(submission.url)
		        	break
		    	else:
			        htmlSource = requests.get(submission.url).text
			        soup = BeautifulSoup(htmlSource)
			        imageUrl = soup.select('.image a')[0]['href']
			        if imageUrl.startswith('//'):
			            imageUrl = 'http:' + imageUrl
			        imageId = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('.')]

			        if '?' in imageUrl:
			            imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
			        else:
			            imageFile = imageUrl[imageUrl.rfind('/') + 1:]

			        localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (sub, submission.id, imageFile)
			        downloadImage(imageUrl, localFileName)
			        break