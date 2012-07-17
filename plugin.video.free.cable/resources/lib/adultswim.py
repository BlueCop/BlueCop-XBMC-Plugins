import urllib, urllib2, re, md5, sys
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common

pluginhandle = int(sys.argv[1])

#CONFIGURATION_URL = 'http://asfix.adultswim.com/staged/configuration.xml'
CONFIGURATION_URL = 'http://asfix.adultswim.com/staged/AS.configuration.xml?cacheID=1326242725288'
#getAllEpisodes = 'http://asfix.adultswim.com/asfix-svc/episodeSearch/getAllEpisodes'
getAllEpisodes = 'http://video.adultswim.com/adultswimdynamic/asfix-svc/episodeSearch/getAllEpisodes'


def masterlist():
    data = common.getURL(CONFIGURATION_URL)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    categories = tree.find('logiccategories').findAll('category')
    db_shows = []
    for category in categories:
        shows = category.findAll('collection')
        for show in shows:
            showid = show['id']
            showname = show['name']#.replace('ZVIP: ','')
            if 'ZVIP:' not in showname:
                db_shows.append((showname, 'adultswim', 'showroot', showid))
    return db_shows

def rootlist():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
    data = common.getURL(CONFIGURATION_URL)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    categories = tree.find('logiccategories').findAll('category')
    for category in categories:
        name = category['name']
        description = category['description']
        categoryid = category['categoryid']
        common.addDirectory(name, 'adultswim', 'showbycat', categoryid)
    common.setView('seasons')             

def showbycat(categoryid=common.args.url):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    data = common.getURL(CONFIGURATION_URL)
    tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    categories = tree.find('logiccategories').findAll('category')
    for category in categories:
        if categoryid == category['categoryid']:
            shows = category.findAll('collection')
            for show in shows:
                showid = show['id']
                showname = show['name'].replace('ZVIP: ','')
                common.addShow(showname, 'adultswim', 'showroot', showid)
    common.setView('tvshows')
              
def showroot(showid=common.args.url):
    common.addDirectory('Clips', 'adultswim', 'showclips', showid)
    listVideos(showid,'TVE,PRE,EPI')
    common.setView('episodes')

def showclips(showid=common.args.url):
    listVideos(showid,'CLI','0','500')
    common.setView('episodes')

def cleanxml(data):
    return unicode(BeautifulStoneSoup(data,convertEntities=BeautifulStoneSoup.XML_ENTITIES).contents[0]).encode( "utf-8" )

def listVideos(CollectionID, filterByEpisodeType, offset='0', limit = '30', sortBy='DESC', sortMethod='sortByDate', categoryName='',showseriestitle=False):
    url = getAllEpisodes
    url += '?limit='+limit
    url += '&offset='+offset
    url += '&'+sortMethod+'='+sortBy
    url += '&categoryName='+categoryName
    url += '&filterByEpisodeType='+filterByEpisodeType
    url += '&filterByCollectionId='+CollectionID
    url += '&networkName=AS'
    data = common.getURL(url)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
    episodes = tree.findAll('episode')
    for episode in episodes:
        showtitle = episode['collectiontitle']
        title = episode['title']
        episodeType = episode['episodetype']
        try:seasonNum = int(episode['episeasonnumber'])
        except:seasonNum = 0
        try:
            episodeNum = episode['episodenumber']
            if episodeNum == '0':
                episodeNum = episode['subepisodenumber']
        except:
            try:episodeNum = episode['subepisodenumber']
            except:episodeNum = '0'
        if len(episodeNum) > 2 and episodeNum.startswith(str(seasonNum)):
            episodeNum = episodeNum[1:]
        if len(episodeNum) > 2:
            episodeNum = episodeNum[-2:]
        episodeNum = int(episodeNum)

        thumbnailUrl = episode['thumbnailurl']
        genre = episode['collectioncategorytype']
        ranking = episode['ranking']
        rating = episode['rating']
        if episode.has_key('originalpremieredate'):
            airDate = episode['originalpremieredate'].replace(' 12:00 AM','').replace('/','-')
        else:
            airDate =  ''
        description = cleanxml(episode.find('description').contents[1].strip())
        segids = episode.find('value').string
        videoid = episode['id']
        if seasonNum <> 0 and episodeNum <> 0:
            name = str(seasonNum)+'x'+str(episodeNum)+' - '+title
        else:
            name = title
            
        if episodeType == 'CLI':
            name += ' (Clip)'
        elif episodeType == 'PRE':
            name += ' (Preview)'
                
        if showseriestitle == True:
            name = showtitle+' - '+name
        if episode.has_key('duration'):
            duration=episode['duration']
        if duration == '':
            segments = episode.findAll('segment')
            duration = 0.00
            for segment in segments:
                    duration += float(segment['duration'])
            duration = str (int(duration/60) )+':'+str( int( duration-int(duration/60)*60 ) )
        u = sys.argv[0]
        if segids is not None:
            u += '?url="'+urllib.quote_plus(segids)+'"'
            u += '&sitemode="playold"'
        else:
            u += '?url="'+urllib.quote_plus(videoid)+'"'
            u += '&sitemode="play"'
        u += '&mode="adultswim"'
        infoLabels={ "Title": title,
                     "TVShowTitle":showtitle,
                     "Season":seasonNum,
                     "Episode":episodeNum,
                     "Plot": description,
                     "Genre":genre,
                     #"Rating":float(ranking),
                     "Mpaa":rating,
                     "Premiered":airDate,
                     "Duration":duration
                     }
        common.addVideo(u,name,thumbnailUrl,infoLabels=infoLabels)            

def play(titleid=common.args.url):
    url = GET_RTMP(titleid)
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)             

def playold(segids=common.args.url):
    segids= segids.split('#')
    stacked_url = 'stack://'
    for segid in segids:
        video = getPlaylist(segid)
        stacked_url += video.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    item = xbmcgui.ListItem(path=stacked_url)
    print stacked_url
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                

def getPlaylist(pid):
    try:
        getVideoPlaylist    = 'http://asfix.adultswim.com/asfix-svc/episodeservices/getVideoPlaylist'
        stime = getServerTime()
        url = getVideoPlaylist + '?id=' + pid + '&r=' + stime
        print 'Adult Swim --> getplaylist :: url = '+url
        #token = stime + '-' + md5.new(stime + pid + '-22rE=w@k4raNA').hexdigest()
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                   'Host': 'asfix.adultswim.com',
                   'Referer':'http://www.adultswim.com/video/ASFix.swf'
                   #'x-prefect-token': token
                   }
        req = urllib2.Request(url,'',headers)    
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        print 'Error error: ', e.error
        return False
    else:
        tree = BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        refs = tree.findAll('ref')
        for ref in refs:
            value = ref.find(attrs={'name' : 'mimeType'})['value']
            if value == 'null' or value == 'video/x-flv':
                return ref['href']

def getServerTime():
    SERVER_TIME_URL  = 'http://asfix.adultswim.com/asfix-svc/services/getServerTime'
    data = common.getURL( SERVER_TIME_URL )
    tree = BeautifulStoneSoup(data)
    return tree.find('time').string

def getAUTH(aifp,window,tokentype,vid,filename):
    authUrl = 'http://www.tbs.com/processors/cvp/token.jsp'
    #authUrl = 'http://www.adultswim.com/astv/mvpd/processors/services/token_embed.do'
    parameters = {'aifp' : aifp,
                  'window' : window,
                  'authTokenType' : tokentype,
                  'videoId' : vid,
                  'profile' : 'adultswim',
                  'path' : filename
                  }
    data = urllib.urlencode(parameters)
    request = urllib2.Request(authUrl, data)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
    response = urllib2.urlopen(request)
    link = response.read(200000)
    response.close()
    return re.compile('<token>(.+?)</token>').findall(link)[0]

def GET_RTMP(vid):
    url = 'http://www.adultswim.com/astv/mvpd/services/cvpXML.do?id='+vid
    html=common.getURL(url)
    tree=BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    sbitrate = int(common.settings['quality'])
    hbitrate = -1
    files = tree.findAll('file')
    for filenames in files:
        try: bitrate = int(filenames['bitrate'])
        except: bitrate = 1
        if bitrate > hbitrate and bitrate <= sbitrate:
            hbitrate = bitrate
            filename = filenames.string
    if 'http://' in filename:
        filename = filename
        return filename
    else:
        filename = filename[1:len(filename)-4]
        serverDetails = tree.find('akamai')
        server = serverDetails.find('src').string.split('://')[1]
        #get auth
        tokentype = serverDetails.find('authtokentype').string
        window = serverDetails.find('window').string
        aifp = serverDetails.find('aifp').string
        auth=getAUTH(aifp,window,tokentype,vid,filename.replace('mp4:',''))      
        #swfUrl = 'http://www.tbs.com/cvp/tbs_video.swf swfvfy=true'
        rtmp = 'rtmpe://'+server+'?'+auth+' playpath='+filename#+" swfurl="+swfUrl
        return rtmp


