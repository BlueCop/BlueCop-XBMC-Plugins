__plugin__ = "cartoon network"
__author__ = "BlueCop,thecheese(orginal boxee version)"
__version__ = "0.0.3"

import urllib, urllib2, re, md5
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulStoneSoup

pluginhandle = int(sys.argv[1])

CONFIGURATION_URL = 'http://www.cartoonnetwork.com/video/staged/CN2.configuration.xml'
getAllEpisodes = 'http://cnvideosvc2.cartoonnetwork.com/svc/episodeSearch/getAllEpisodes'


#lists initial categories and caches them
def listCategories():
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
        addDir('Full Episodes', 'full', 4)
        addDir('Clips', 'clips', 4)
        data = getURL(CONFIGURATION_URL)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        categories = tree.find('logiccategories').findAll('category')
        for category in categories:
                name = category['name']
                description = category['description']
                categoryid = category['categoryid']
                addDir(name, categoryid, 1, description)
                

        
#lists shows for a particular category
def listShowsByCat(categoryid):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        data = getURL(CONFIGURATION_URL)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        categories = tree.find('logiccategories').findAll('category')
        for category in categories:
                if categoryid == category['categoryid']:
                        shows = category.findAll('collection')
                        for show in shows:
                                showid = show['id']
                                name = show['name']
                                addDir(name, showid, 2)

#lists episodes by show id              
def showRoot(showid):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        addDir('Clips', showid, 3)
        listVideos(showid,'PRE-PRE,EPI-EPI')

#lists Clips by show id 
def showClips(showid):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        listVideos(showid,'CLI-CLI','0','500')                

def browseAll(url):
        if url == 'full':
                listVideos('','PRE-PRE,EPI-EPI','0','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                listVideos('','PRE-PRE,EPI-EPI','30','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                listVideos('','PRE-PRE,EPI-EPI','60','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                listVideos('','PRE-PRE,EPI-EPI','90','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                #listVideos('','PRE,EPI','120','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                #listVideos('','PRE,EPI','150','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                #listVideos('','PRE,EPI','180','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
        elif url == 'clips':
                listVideos('','CLI-CLI','0','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                listVideos('','CLI-CLI','30','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                listVideos('','CLI-CLI','60','30',sortMethod='sortByEpisodeRanking',showseriestitle=True)
                listVideos('','CLI-CLI','90','30',sortMethod='sortByEpisodeRanking',showseriestitle=True) 

#lists episodes
def listVideos(CollectionID, filterByEpisodeType, offset='0', limit = '50', sortBy='DESC', sortMethod='sortByDate', categoryName='',showseriestitle=False):
        url = getAllEpisodes
        url += '?networkName=CN2'
        url += '&limit='+limit
        url += '&offset='+offset
        url += '&'+sortMethod+'='+sortBy
        url += '&categoryName='+categoryName
        url += '&filterByEpisodeType='+filterByEpisodeType
        url += '&filterByCollectionId='+CollectionID
        data = getURL(url)
        tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes = tree.findAll('episode')
        for episode in episodes:
                showtitle = episode['collectiontitle']
                title = episode['title']
                episodeType = episode['episodetype']
                try:
                        seasonNum = int(episode['episeasonnumber'])
                except:
                        seasonNum = 0
                try:
                        episodeNum = int(episode['episodenumber'])
                except:
                        episodeNum = 0
                thumbnailUrl = episode['thumbnailurl']
                genre = episode['collectioncategorytype']
                ranking = episode['ranking']
                rating = episode['rating']
                expirationDate = episode['expirationdate']
                description = episode.find('description').contents[1].strip()
                segids = episode.find('value').string
                if seasonNum == 0 or episodeNum == 0:
                        name = title
                        if episodeType == 'CLI-CLI':
                                name += ' (Clip)'
                        elif episodeType == 'PRE-PRE':
                                name += ' (Preview)'
                elif episodeType == 'EPI-EPI':
                        name = str(seasonNum)+'x'+str(episodeNum)+' - '+title
                elif episodeType == 'CLI-CLI':
                        name = title+' (Clip from '+str(seasonNum)+'x'+str(episodeNum)+')'
                elif episodeType == 'PRE-PRE':
                        name = title+' (Preview for '+str(seasonNum)+'x'+str(episodeNum)+')'
                if showseriestitle == True:
                        name = showtitle+' - '+name
                segments = episode.findAll('segment')
                duration = 0.00
                for segment in segments:
                        duration += float(segment['duration']) 
                u=sys.argv[0]+"?url="+urllib.quote_plus(segids)+"&mode="+str(10)
                item=xbmcgui.ListItem(name, iconImage=thumbnailUrl, thumbnailImage=thumbnailUrl)
                item.setInfo( type="Video", infoLabels={ "Title": title,
                                                         "TVShowTitle":showtitle,
                                                         "Season":seasonNum,
                                                         "Episode":episodeNum,
                                                         "Plot": description,
                                                         "Genre":genre,
                                                         "Rating":float(ranking),
                                                         "Mpaa":rating,
                                                         "Premiered":expirationDate,
                                                         "Duration":str(int(duration/60))
                                                         })
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item)
                

def getVideoURL(segids):
        getPlaylist
        segids= segids.split('#')
        stacked_url = 'stack://'
        for segid in segids:
                video = getPlaylist(segid)
                stacked_url += video.replace(',',',,')+' , '
        stacked_url = stacked_url[:-3]
        item = xbmcgui.ListItem(path=stacked_url)
        print stacked_url
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                
	
def getURL( url, data=None, token=None):
        print url
        headers = { 
                'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                'Referer':'http://www.cartoonnetwork.com/video/VideoBrowser.swf'
        }
        if data:
                data = urllib.urlencode(data)
        if token:
                headers['x-prefect-token'] = token
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data

def getPlaylist(pid):
        try:
                getVideoPlaylist    = 'http://cnvideosvc2.cartoonnetwork.com/svc/episodeservices/getVideoPlaylist?networkName=CN2'
                stime = getServerTime()
                url = getVideoPlaylist + '&id=' + pid + '&r=' + stime
                print 'Adult Swim --> getplaylist :: url = '+url
                token = stime + '-' + md5.new(stime + pid + '-22rE=w@k4raNA').hexdigest()
                headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                           'Host': 'cnvideosvc2.cartoonnetwork.com',
                           'Referer':'http://www.cartoonnetwork.com/video/VideoBrowser.swf',
                           'x-prefect-token': token
                           }
                req = urllib2.Request(url,'',headers)    
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
        except urllib2.URLError, e:
                print 'Error reason: ', e.reason
                return False
        else:
                tree = BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
                refs = tree.findAll('ref')
                for ref in refs:
                        value = ref.find(attrs={'name' : 'mimeType'})['value']
                        if value == 'null' or value == 'video/x-flv':
                                return ref['href']

def getServerTime():
        SERVER_TIME_URL  = 'http://cnvideosvc2.cartoonnetwork.com/svc/services/getServerTime?networkName=CN'
        data = getURL( SERVER_TIME_URL )
        tree = BeautifulStoneSoup(data)
        return tree.find('time').string


"""
        addDir()
"""
def addDir(name, url, mode, plot='', iconimage='DefaultFolder.png'):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        if plot:
                liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
        else:
                liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok



"""
        getParams()
        grab parameters passed by the available functions in this script
"""
def getParams():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param

def qs2dict(qs):
    try:
        params = dict([part.split('=') for part in qs.split('&')])
    except:
        params = {}
    return params


#grab params and assign them if found
params=getParams()
url=None
name=None
mode=None
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

#print params to the debug log
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

#check $mode and execute that mode
if mode==None or url==None or len(url)<1:
        print "CATEGORY INDEX : "
        listCategories()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==1:
        listShowsByCat(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
        showRoot(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
        showClips(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==4:
        browseAll(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==10:
        getVideoURL(url)

