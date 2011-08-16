import urllib, urllib2, re, md5, sys
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from BeautifulSoup import BeautifulStoneSoup
import resources.lib._common as common

pluginhandle = int(sys.argv[1])

CONFIGURATION_URL = 'http://asfix.adultswim.com/staged/configuration.xml'
getAllEpisodes = 'http://asfix.adultswim.com/asfix-svc/episodeSearch/getAllEpisodes'

def masterlist():
        data = common.getURL(CONFIGURATION_URL)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        categories = tree.find('logiccategories').findAll('category')
        db_shows = []
        for category in categories:
                shows = category.findAll('collection')
                for show in shows:
                        showid = show['id']
                        showname = show['name']
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
                
        

def showbycat(categoryid=common.args.url):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        data = common.getURL(CONFIGURATION_URL)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        categories = tree.find('logiccategories').findAll('category')
        for category in categories:
                if categoryid == category['categoryid']:
                        shows = category.findAll('collection')
                        for show in shows:
                                showid = show['id']
                                showname = show['name']
                                common.addDirectory(showname, 'adultswim', 'showroot', showid)

              
def showroot(showid=common.args.url):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        common.addDirectory('Clips', 'adultswim', 'showclips', showid)
        listVideos(showid,'PRE,EPI')


def showclips(showid=common.args.url):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        listVideos(showid,'CLI','0','500')


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
                expirationDate = episode['expirationdate'].replace(' 12:00 AM','')
                description = cleanxml(episode.find('description').contents[1].strip())
                segids = episode.find('value').string
                if seasonNum == 0 or episodeNum == 0:
                        name = title
                        if episodeType == 'CLI':
                                name += ' (Clip)'
                        elif episodeType == 'PRE':
                                name += ' (Preview)'
                elif episodeType == 'EPI':
                        name = str(seasonNum)+'x'+str(episodeNum)+' - '+title
                elif episodeType == 'CLI':
                        name = title+' (Clip from '+str(seasonNum)+'x'+str(episodeNum)+')'
                elif episodeType == 'PRE':
                        name = title+' (Preview for '+str(seasonNum)+'x'+str(episodeNum)+')'
                if showseriestitle == True:
                        name = showtitle+' - '+name
                segments = episode.findAll('segment')
                duration = 0.00
                for segment in segments:
                        duration += float(segment['duration'])
                u = sys.argv[0]
                u += '?url="'+urllib.quote_plus(segids)+'"'
                u += '&mode="adultswim"'
                u += '&sitemode="play"'
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
                

def play(segids=common.args.url):
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
                token = stime + '-' + md5.new(stime + pid + '-22rE=w@k4raNA').hexdigest()
                headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                           'Host': 'asfix.adultswim.com',
                           'Referer':'http://www.adultswim.com/video/ASFix.swf',
                           'x-prefect-token': token
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


