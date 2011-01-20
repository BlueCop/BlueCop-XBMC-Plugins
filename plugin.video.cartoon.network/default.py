'''
        [adult swim] v0.2 for XBMC
                
'''

__plugin__ = "[adult swim]"
__author__ = "thecheese,BlueCop(XBMC fixes and updated)"
__url__ = ""
__svn__ = ""
__version__ = "0.3"

import urllib, urllib2, re, md5
import string, os, time, datetime
import xbmc, xbmcgui, xbmcplugin
from adultswim_api import *


#grab to root directory and assign the image forlder a var
rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
imageDir = os.path.join(rootDir, 'resources', 'thumbnails') + '/'
resourceDir = os.path.join(rootDir, 'resources')

pluginhandle = int(sys.argv[1])


def listCategories():
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        aswim = AdultSwim()
        categories = aswim.getCategories()
        for category in categories:
                shows = aswim.getShowsByCategory( category['id'] )
                for show in shows:
                        addDir(show['name'], 'showTypes?id='+show['id'], 3 , 'DefaultFolder.png') 
        

def listShowsByCat(url):
        xbmcplugin.setContent(pluginhandle, 'shows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        aswim = AdultSwim()
        params = qs2dict(url.split('?')[1])
        shows = aswim.getShowsByCategory( params['cid'] )
        for show in shows:
                addDir(show['name'], 'showTypes?id='+show['id'], 3 , 'DefaultFolder.png')

             
def showTypes(showid):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        aswim = AdultSwim()
        url = showid+'&filterByEpisodeType=PRE,EPI'
        params = qs2dict(url.split('?')[1])
        episodes = aswim.getEpisodesByShow( params['id'])        
        if len(episodes) == 0:
                url = showid+'&filterByEpisodeType=CLI'
                params = qs2dict(url.split('?')[1])
                episodes = aswim.getEpisodesByShow( params['id'])
                for episode in episodes:
                        name = episode['title']+' (Clip)'
                        addLink(name,
                                'initEpisode?ids='+episode['id'],
                                5,
                                episode['thumbnail'],
                                episode['description']
                                #episode['collectionTitle'],
                                #episode['collectionCategoryType'],
                                )
                return

        for episode in episodes:
                if episode['episodeType'] <> 'CLI':
                        name = episode['epiSeasonNumber']+'x'+episode['episodeNumber']+' - '+episode['title']
                        addLink(name,
                                'initEpisode?ids='+episode['id'],
                                5,
                                episode['thumbnail'],
                                episode['description'])
        

        #addDir(" Clips", showid+'&filterByEpisodeType=CLI', 4 , 'DefaultFolder.png', 'Clips')

        #addDir(" Full Episodes", url+'&filterByEpisodeType=PRE,EPI', 4 , imageDir + 'video.png', 'Full Episodes')


#lists episodes by show id
def listEpisodes(url):
        aswim = AdultSwim()
        params = qs2dict(url.split('?')[1])
        episodes = aswim.getEpisodesByShow( params['id'], params['filterByEpisodeType'] )
        
        if len(episodes) == 0:
                xbmcgui.Dialog().ok("[adult swim]", "No entries found.")
                return

        for episode in episodes:
                name = episode['title']+' (Clip)'
                addLink(name,
                        'initEpisode?ids='+episode['id'],
                        5,
                        episode['thumbnail'], episode['description'])


def getVideoURL(id):
        params = qs2dict(url.split('?')[1])
        aswim = AdultSwim()
        episodes = aswim.getEpisodesByIDs( params['ids'] )
        stacked_url = 'stack://'
        for episode in episodes:
                for segment in episode['segments']:
                        response = aswim.getPlaylist(segment['id'])
                        match = re.compile('href="(.+?)"').findall(response)
                        title = episode['collectionTitle'] + ' - ' + episode['title']
                        stacked_url += match[0].replace(',',',,')+' , '
        stream = 'true'#httpDownload(playlist_urls,name)
        if stream == 'false':
                return
        stacked_url = stacked_url[:-3]
        item = xbmcgui.ListItem(path=stacked_url)
        print stacked_url
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def httpDownload( playlist_urls, name):
        def Download(url,dest):
                    dp = xbmcgui.DialogProgress()
                    dp.create('Downloading','',name)
                    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
                    try:
                                    percent = min((numblocks*blocksize*100)/filesize, 100)
                                    dp.update(percent)
                    except:
                                    percent = 100
                                    dp.update(percent)
                    if dp.iscanceled():
                                    dp.close()
        flv_file = None
        stream = 'false'
        C = 0
        if (xbmcplugin.getSetting(pluginhandle,'download') == '0'):
                dia = xbmcgui.Dialog()
                ret = dia.select(xbmc.getLocalizedString( 30011 ),[xbmc.getLocalizedString( 30006 ),xbmc.getLocalizedString( 30007 ),xbmc.getLocalizedString( 30008 ),xbmc.getLocalizedString( 30012 )])
                if (ret == 0):
                        stream = 'true'
                elif (ret == 1):
                        for url in playlist_urls:
                                C = C + 1
                                flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name+'-part'+str(C)+'.flv'))
                                Download(url,flv_file)
                elif (ret == 2):
                        for url in playlist_urls:
                                C = C + 1
                                flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name+'-part'+str(C)+'.flv'))
                                Download(url,flv_file)
                        stream = 'true'
                else:
                        return stream
        #Play
        elif (xbmcplugin.getSetting(pluginhandle,'download') == '1'):
                stream = 'true'
        #Download
        elif (xbmcplugin.getSetting(pluginhandle,'download') == '2'):
                for url in playlist_urls:
                        C = C + 1
                        flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name+'-part'+str(C)+'.flv'))
                        Download(url,flv_file)
        #Download & Play
        elif (xbmcplugin.getSetting(pluginhandle,'download') == '3'):
                for url in playlist_urls:
                        C = C + 1
                        flv_file = xbmc.translatePath(os.path.join(xbmcplugin.getSetting(pluginhandle,'download_Path'), name+'-part'+str(C)+'.flv'))
                        Download(url,flv_file)
                stream = 'true'            
        if (flv_file != None and os.path.isfile(flv_file)):
                finalurl =str(flv_file)
        return stream


"""
        addLink()
"""
def addLink(name,url,mode,iconimage, plot=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        if plot:
                liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
        else:
                liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok


"""
        addDir()
"""
def addDir(name,url,mode,iconimage, plot=''):
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
elif mode==2:
        listShowsByCat(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
        showTypes(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==4:
        listEpisodes(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]),cacheToDisc=True)
elif mode==5:
        getVideoURL(url)

