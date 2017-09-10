import sys
import re
from urllib2 import urlopen as uo
from bs4 import BeautifulSoup as soup
import os.path

if len(sys.argv) > 1:
	my_url = sys.argv[1]
else:
	my_url = "http://gaana.com/playlist/gaana-dj-pyaar-ka-pehla-proposal"
print my_url
uclient = uo(my_url)
page_html = uclient.read()
uclient.close()
page_soup = soup(page_html, "html.parser")

containers = page_soup.findAll("div",{"class":"lastend-container details-list-paddingnone content-container artworkload"})
len(containers)
contain = containers[0]
song = contain.findAll("div",{"class":"track_npqitemdetail"})

playlist = page_soup.findAll("div",{"class":"_d_t_det _d_tp_det"})
playlist[0].h1.text
os.mkdir(playlist[0].h1.text)
os.chdir(playlist[0].h1.text)

filename = playlist[0].h1.text + ".csv"
fcsv = open(filename, "w")
headers = "title, artist\n"
fcsv.write(headers)
for s in song:
	try:
		title = s.h2.text
		artist = s.p.text.split("-")[1].strip() 
		movie = s.p.text.split("-")[0].strip()
		print title + "," + movie + "," + artist + "\n"

		fcsv.write(title + "," + movie + "," + artist + "\n")
		link = "http://mymp3song.org/files/search/sort/download/find/" + movie.replace(" ",'+')
		print link

		uclient = uo(link)
		page_html = uclient.read()
		uclient.close()
		mymp3 = soup(page_html, "html.parser")
		maindiv = mymp3.findAll("div",{"id":"mainDiv"})
		md = maindiv[0]
		song_list = md.findAll("a",{"class":"fileName"})
		for ss in song_list:
			p = ss.findAll(text=re.compile(title,re.IGNORECASE))
			if p:
				d_page = "http://mymp3song.org" + ss['href']
				break
		uclient = uo(d_page)
		page_html = uclient.read()
		uclient.close()
		dl_page = soup(page_html, "html.parser")

		dl = dl_page.findAll("div",{"class":"fi"})
		url = "http://mymp3song.org" + dl[0].a['href']
		

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
		    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		    status = status + chr(8)*(len(status)+1)
		    print status
		f.close()
	except Exception:
		pass
fcsv.close()
