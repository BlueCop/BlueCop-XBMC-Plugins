import urllib, urllib2
import os, re, sys, md5, string
import xbmc, xbmcgui, xbmcplugin

from elementtree.ElementTree import *

media="http://search.yahoo.com/mrss/"
atom="http://www.w3.org/2005/Atom"
opensearch="http://a9.com/-/spec/opensearch/1.1/"


########################################################################################
#####################################    COMMON    #####################################       
########################################################################################

def getURL( url ):
        try:
                print 'MTVN --> getURL :: url = '+url
                req = urllib2.Request(url)
                req.addheaders = [('Referer', 'http://www.mtv.com'),
                                  ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7)')]
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
        except urllib2.URLError, e:
                error = 'Error code: '+ str(e.code)
                xbmcgui.Dialog().ok(error,error)
                print 'Error code: ', e.code
                return False
        else:
                return link

def parseapiVideos(response):
        if response == False:
                return False
        tree1 = ElementTree(fromstring(response))
        videos = []
        for entry in tree1.getroot().findall('{%s}entry' % atom):
                video = []
                m = entry.find('{%s}content' % media)
                video.append(m.get('url').split('/')[-1])
                name = entry.find('{%s}description' % media).text
                name = name.split('|')[0] + '-' + name.split('|')[1]
                video.append(name)
                turl = [0,'url']
                for t in entry.findall('{%s}thumbnail' % media):
                        url = t.get('url')
                        width = t.get('width')
                        height = t.get('height')
                        w = int(width)
                        h = int(height)
                        pixels = w*h
                        if pixels > turl[0]:
                                turl[0] = pixels
                                turl[1] = url
                if turl[1] <> 'url':               
                        video.append(turl[1])
                else:
                        video.append('')
                videos.append(video)
        return videos

def parseapiArtists(response):
        if response == False:
                return False
        tree1 = ElementTree(fromstring(response))
        artists = []
        for entry in tree1.getroot().findall('{%s}entry' % atom):
                artist = []
                artist.append(entry.find('{%s}id' % atom).text)
                artist.append(entry.find('{%s}title' % atom).text)
                turl = [0,'url']
                for t in entry.findall('{%s}thumbnail' % media):
                        url = t.get('url')
                        width = t.get('width')
                        height = t.get('height')
                        w = int(width)
                        h = int(height)
                        pixels = w*h
                        if pixels > turl[0]:
                                turl[0] = pixels
                                turl[1] = url
                if turl[1] <> 'url':               
                        artist.append(turl[1])
                else:
                        artist.append('')
                artists.append(artist)
        return artists

#Universal Parameters
#max-results:   Limit the maximum number of results. The default value is 25. The maximum value is 100 	25, 1-100
#example:       ?max-results=25
        
#start-index:   Choose the first result to display in the returns. The first return is
#                       1. When used with the max-results parameter, multiple pages of results can be created.
#                       1, numeric value
#example:       ?start-index=26

#date: 	        Limit the returns to date range specified.	MMDDYYYY-MMDDYYYY
#example:       ?date=01011980-12311989

#sort:          Specifies the sort order for returns.	relevance, date_ascending, date_descending
#example:       ?sort=date_ascending

########################################################################################
#####################################     VIDEO     ####################################       
########################################################################################


#Requires parameters term ?term=
#Returns a list of videos for a specific search term.
def videoSearch(term):
        VideoSearch = 'http://api.mtvnservices.com/1/video/search/'
        term = '"'+term+'"'
        encode = urllib.quote_plus(term)
        url = VideoSearch +'?term='+ encode
        response = getURL(url)
        return parseapiVideos(response)

#Returns videos associated to a specific artist.
def artistVideos(artist):
        #ArtistVideos = 'http://api.mtvnservices.com/1/artist/[artist_uri]/videos'
        #url = ArtistVideos.replace('[artist_uri]',artist)
        url = artist+'videos/'
        response = getURL(url)
        return parseapiVideos(response)

#Returns a single video by encoded ID.
def videoMethod(videoid):
        VideoMethod = 'http://api.mtvnservices.com/1/video/[video_id]/'
        return video

########################################################################################
#####################################     ARTIST    ####################################       
########################################################################################


#Returns content associated to a specific artist.
def artistAlias(artist):
        ArtistAlias = 'http://api.mtvnservices.com/1/artist/[artist_alias]/'
        return artist

#Requires parameters term ?term=
#Returns a list of artists for a specific search term.
def artistSearch(term):
        ArtistSearch = 'http://api.mtvnservices.com/1/artist/search/'
        term = '"'+term+'"'
        encode = urllib.quote_plus(term)
        url = ArtistSearch +'?term='+ encode
        print url
        response = getURL(url)
        return parseapiArtists(response)

#Retrieves a list of artists sorted alphabetically.
# a-z and '-' for begining with numbers
def artistBrowse(letter):
        ArtistBrowse = 'http://api.mtvnservices.com/1/artist/browse/[alpha]'
        url = ArtistBrowse.replace('[alpha]',letter)
        response = getURL(url)
        return parseapiArtists(response)

#Returns a list of artists related to the specified artist.
def relatedArtists(artist):
        #RelatedArtist = 'http://api.mtvnservices.com/1/artist/[artist_uri]/related/'
        #url = RelatedArtist.replace('[artist_uri]',artist)
        url = artist+'related/'
        response = getURL(url)
        return parseapiArtists(response)

########################################################################################
######################################    GENRE     ####################################       
########################################################################################

#Returns content links for a specified genre.
def genreAlias(genre):
        GenreAlias = 'http://api.mtvnservices.com/1/genre/[genre_alias]/'

#Returns a list of artists for a specified genre.
def genreArtists(genre,maxitems,startindex,sort):
        GenreArtists = 'http://api.mtvnservices.com/1/genre/[genre_alias]/artists/'
        url = GenreArtists.replace('[genre_alias]',genre) + "?max-results=" + str(maxitems) + "&start-index=" + str(startindex) + "&sort=" + sort
        response = getURL(url)
        return parseapiArtists(response)

#Returns a list of videos for a specified genre.
def genreVideos(genre,maxitems,startindex,sort):
        GenreVideos = 'http://api.mtvnservices.com/1/genre/[genre_alias]/videos/'
        url = GenreVideos.replace('[genre_alias]',genre) + "?max-results=" + str(maxitems) + "&start-index=" + str(startindex) + "&sort=" + sort
        response = getURL(url)
        return parseapiVideos(response)

########################################################################################
#####################################    MTV.COM    ####################################       
########################################################################################
#MTV.com video lists.

def VideoPicksMTV():
        url = 'http://www.mtv.com/music/video/'
        response = getURL(url)
        if response == False:
                return False
        response = response.replace('\n',' ')
        data = re.compile('<a href="/videos/(.+?)"> <img src="(.+?)".+?> <span class="icon icon-play">Video: </span>(.+?)</a>').findall(response)
        videos = []
        for vid, thumb, artist in data:
                video = []
                vid = 'mgid:uma:video:api.mtvnservices.com:' + vid.split('/')[1]
                video.append(artist.replace('"',''))
                video.append("http://www.mtv.com" + thumb)
                video.append(vid)
                videos.append(video)
        return videos

def VideoPremieresMTV():
        url = 'http://www.mtv.com/music/videos/premieres/'
        response = getURL(url)
        if response == False:
                return False
        response = response.replace('\n',' ')
        data = re.compile('<a href="/videos/(.+?)"> <img src="(.+?)".+?> <span class="icon icon-play">Video: </span>(.+?)</a>').findall(response)
        videos = []
        for vid, thumb, artist in data:
                video = []
                vid = 'mgid:uma:video:api.mtvnservices.com:' + vid.split('/')[1]
                video.append(artist.replace('"',''))
                video.append("http://www.mtv.com" + thumb)
                video.append(vid)
                videos.append(video)
        return videos

def VideoPopularMTV():
        url = 'http://www.mtv.com/music/video/popular.jhtml'
        response = getURL(url)
        if response == False:
                return False
        response = response.replace('\n',' ')
        data = re.compile('<a href="/videos/\?vid=(.+?)"> <img src="(.+?)".+?> <span class="icon icon-play">Video: </span>(.+?)</a>').findall(response)
        videos = []
        for vid, thumb, artist in data:
                video = []
                vid = 'mgid:uma:video:api.mtvnservices.com:' + vid
                video.append(artist)
                video.append("http://www.mtv.com" + thumb)
                video.append(vid)
                videos.append(video)
        return videos


########################################################################################
####################################      RTMP      ####################################       
########################################################################################

def getrtmp(uri):
        print uri
        smilurl = 'http://api-media.mtvnservices.com/player/embed/includes/mediaGen.jhtml?uri='+uri+'&vid='+uri.split(':')[4]+'&ref={ref}'
        smil = getURL(smilurl)
        if smil == False:
                return False
        urls = re.compile('<src>(.+?)</src>').findall(smil)
        rtmps = []
        for rtmpurl in urls:
                if 'rtmp' in rtmpurl:
                        rtmpurl =rtmpurl.replace('rtmpe','rtmp')
                        rtmpurl = rtmpurl.replace('rtmp://','')
                        rtmpsplit = rtmpurl.split('/ondemand/')
                        rtmphost = rtmpsplit[0]
                        playpath = rtmpsplit[1]
                        if '.flv' in playpath:
                                playpath = playpath.replace('.flv','')
                        elif '.mp4' in playpath:
                                playpath = 'mp4:'+ playpath.replace('.mp4','')
                        app = 'ondemand' 
                        identurl = 'http://'+rtmphost+'/fcs/ident'
                        ident = getURL(identurl)
                        ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
                        rtmpurl = 'rtmpe://'+ip+'/'+app+'?_fcs_vhost='+rtmphost
                        rtmp = []
                        rtmp.append(rtmpurl)
                        rtmp.append(playpath)
                        rtmps.append(rtmp)
                else:
                        print rtmpurl
        return rtmps

# Needs updating to retrive current version from server
def getswfUrl():
        swfUrl = "http://media.mtvnservices.com/player/release/?v=4.4.3"
        return swfUrl
