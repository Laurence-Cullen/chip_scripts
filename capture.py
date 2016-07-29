import urllib
url_choice = 'http://bl24i-di-serv-01.diamond.ac.uk:8082/cam3.MJPG.jpgh/axis-cgi/jpg/image.cgi?resolution=4CIF'
current_image = urllib.urlopen(url_choice)
fid = 'laurence.jpg'
g = open(fid, 'w')
g.write(current_image.read())
g.close()
