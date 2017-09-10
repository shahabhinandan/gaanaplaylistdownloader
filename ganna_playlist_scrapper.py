#############################################
#	Gaana Playlist Downloader - v 0.3		#
#			Author: abhioxic				#
#		  Free to use GPL v3				#
#############################################

import sys
import re
from urllib2 import urlopen as uo
from bs4 import BeautifulSoup as soup
import os.path
import pyperclip

# Check if any agruments are provided or not, else copy from clipboard.
# TODO: Sanitation
if len(sys.argv) > 1:
	my_url = sys.argv[1]
else:
	my_url = pyperclip.paste()
print "Downloading " + my_url

uclient = uo(my_url)
page_html = uclient.read()
uclient.close()
page_soup = soup(page_html, "html.parser")

# This div contains the track list and all other information we need. As of Sept 10 '17.
## TODO: Try catch and create function man!
containers = page_soup.findAll("div",{"class":"lastend-container details-list-paddingnone content-container artworkload"})
contain = containers[0]

# Gets Playlist name
# TODO: Sanitation!!!
playlist = page_soup.findAll("div",{"class":"_d_t_det _d_tp_det"}) 

# Creates a folder with playlist' name
try:
	os.mkdir(playlist[0].h1.text)
except Exception:
	pass
os.chdir(playlist[0].h1.text)

# Creates a csv file. Contains Title, Movie, Artists and weather it is downlaoded or not.
filename = playlist[0].h1.text + ".csv"
fcsv = open(filename, "w")
headers = "Title, Movie, Artist, Download\n"
fcsv.write(headers)

# Each track's master div
song = contain.findAll("div",{"class":"track_npqitemdetail"})
for s in song:
	try:
		title = s.h2.text.replace(","," & ").strip()
		artist = s.p.text.split("-")[1].strip().replace(","," | ")
		movie = s.p.text.split("-")[0].strip().replace(","," | ")
		#print "Got " + title + "," + movie + "," + artist

		# Searches the *movie name* on mymp3song. Because searching title gives remixes too and I don't want that ( also hard to prune).
		fcsv.write(title + "," + movie + "," + artist)
		searchlink = "http://mymp3song.org/files/search/sort/download/find/" + movie.replace(" ",'+')
		#print "Going to " + searchlink

		uclient = uo(searchlink)
		page_html = uclient.read()
		uclient.close()
		s_link = soup(page_html, "html.parser")

		mymp3_search_result_list = s_link.findAll("div",{"id":"mainDiv"})
		md = mymp3_search_result_list[0]
		
		# This tag with class fileName is the each search-result list item. I am terrible with descriptions.
		mymp3_song_list = md.findAll("a",{"class":"fileName"})
		for ss in mymp3_song_list:
			p = ss.findAll(text=re.compile(title,re.IGNORECASE)) # Finds the list item which regex matches the song title.
			if p:
				download_page = "http://mymp3song.org" + ss['href'] # The href tags contains the link to download.
				#print "download_page is " + download_page
				break

		# Looking at the url you might think that you can directly generate 
		# download link as it simply uses the file id which you already have
		# But, the link actually changes depending on wheather there are more
		# than one bitrate available for the file. So better use this.

		uclient = uo(download_page)
		page_html = uclient.read()
		uclient.close()
		dl_page = soup(page_html, "html.parser")

		# url has the final download link
		dl = dl_page.findAll("div",{"class":"fi"})
		url = "http://mymp3song.org" + dl[0].a['href']
		#print "Url donwloading is " + url

		file_name = title + " - " + movie + ".mp3"
		u = uo(url)
		f = open(file_name, 'wb')
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s Bytes: %s" % (file_name, file_size)

		file_size_dl = 0
		block_sz = 8192
		while True:
		    buffer = u.read(block_sz)
		    if not buffer:
		        break

		    file_size_dl += len(buffer)
		    f.write(buffer)
		    # status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		    # status = status + chr(8)*(len(status)+1)
		print "Downloaded" + "\n"
		fcsv.write(",Downloaded\n") # Finally, adds 'Downloaded' to the csv.
		f.close()
		# This is important else it will downlaod the same song with different names.
		del download_page 
	except Exception:
		fcsv.write("\n") # If failed to downlaod, the last column is left blank.
		pass
fcsv.close()

# TODO: