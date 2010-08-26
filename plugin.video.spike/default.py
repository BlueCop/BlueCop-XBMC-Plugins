import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, sys, os, time

baseurl = 'http://www.spike.com'
pluginhandle = int(sys.argv[1])

def getHTML( url ):
        try:
                print 'Spike --> getHTML :: url = ' + url
                req = urllib2.Request(url)
                req.addheaders = [('Referer', 'http://spike.com'),
                                  ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
        except urllib2.URLError, e:
                print 'Error code: ', e.code
                return False
        else:
                return link

def SHOWS():
        url = baseurl + '/shows/?tab=alphabetical'
        items = getHTML(url)
        shows=re.search('<ul id="showlist">.+?<div id="CONTENT" class="clearfix">', items, re.DOTALL).group(0)
        shows=re.compile('<h3>\s*<a href="(.+?)" title="(.+?)">(.+?)</a>\s*</h3>\s*<a href="(.+?)" class="show_frame"><img src="(.+?)"').findall(shows, re.DOTALL)
        for category, showname, name2, category2, thumb in shows:
                if showname == "Guys Choice 2010" or "2009" in showname or "The Ultimate" in showname:
                        continue
                showname = showname.replace('&amp;','&').replace('&#039;',"'")
                category = baseurl + category
                addDir(str(showname),category,1,thumb)

def SHOWROOT(url):
        items = getHTML(url)
        tabs = shows=re.search('<ul id="section-tabs" class="clearfix">.+?</ul>', items, re.DOTALL).group(0)
        videos = re.compile('<a href="(.+?)"  id="(.+?)">(.+?)</a></li>').findall(tabs, re.DOTALL)
        for url,collectionid,name in videos:
                url = baseurl + url
                if name == 'Full Episodes' or name == 'Full Episode' or name == 'Episodes':
                        LISTVIDEOS(url)
                elif 'Blog' in name or 'Games' in name or 'Articles' in name or 'Home' in name or 'Poll' in name or 'Photos' in name or 'Comic' in name or 'Game' in name or 'Loads' in name or 'Checklists' in name or 'Bio' in name:
                        continue
                else:
                        addDir(name,url,2,'')


def LISTVIDEOS(url):
        xbmcplugin.setContent(pluginhandle, 'episodes')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
        items = getHTML(url)
        shows=re.compile('<a href="(.+?)" class="tn_frame clearfix musicvideos" title="(.+?)">\s*<img src="(.+?)"').findall(items, re.DOTALL)
        for episode,name,thumb in shows:
                name = name.replace('&amp;','&').replace('&#039;',"'")
                episode = baseurl + episode
                addLink(str(name),episode,3,thumb)


def VIDEOLINKS(url,name):
        items = getHTML(url)
        try:
                configurl=re.compile('\("CONFIG_URL", (.+?)\);').findall(items)[0]
        except:
                configurl = re.compile('<param name="flashvars" value="CONFIG_URL=(.+?)"').findall(items)[0]
        configurl = configurl.replace('"','')
        print 'CONFIG_URL:\t' + str(configurl)
        url = baseurl + configurl.replace('%26','&')
        configxml = getHTML(url)
        mrssurl = re.compile('<feed>(.+?)</feed>').findall(configxml, re.DOTALL)
        if 'endOfPlayRelatedList' in mrssurl[0]:
                mrssurl = mrssurl[1]
        else:
                mrssurl = mrssurl[0]
        mrssurl = mrssurl.replace('&amp;','&')
        ifilmid = re.compile('ifilmId=(.+?)\&').findall(mrssurl)
        mrssxml = getHTML(mrssurl)
        match=re.compile("<media:content type='text/xml' medium='video' isDefault='true' duration='(.+?)' url='(.+?)'").findall(mrssxml)
        stacked_url = 'stack://'
        for param,guid in match:
                items = getHTML(guid)
                videos=re.compile('<src>(.+?)</src>').findall(items, re.DOTALL)
                print len(videos)
                if len(videos) == 1:
                        for link in videos:
                                link = link.replace('&amp;','&')
                                stacked_url += link.replace(',',',,')+' , '
                else:
                        segments = []
                        for link in videos:
                                link = link.replace('&amp;','&')
                                if '_1200.flv' in link and (xbmcplugin.getSetting(pluginhandle,"quality") == '0'):
                                        segments.append(link)
                                elif '_700.flv' in link and (xbmcplugin.getSetting(pluginhandle,"quality") == '1'):
                                        segments.append(link)
                                elif '_300.flv' in link and (xbmcplugin.getSetting(pluginhandle,"quality") == '2'):
                                        segments.append(link)
                        for url in segments:
                                swfUrl = "http://media.mtvnservices.com/player/release/?v=4.5.3"
                                rtmpurl = url + " swfurl=" + swfUrl + " swfvfy=true"
                                stacked_url += rtmpurl.replace(',',',,')+' , '
        stacked_url = stacked_url[:-3]
        print 'FINAL URL'
        print stacked_url
        item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='', path=stacked_url)
        item.setInfo( type="Video",infoLabels={ "Title": name})
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)


def get_params():
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

def addLink(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
              
params=get_params()
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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        SHOWS()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==1:
        print ""+url
        SHOWROOT(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
        print ""+url
        LISTVIDEOS(url)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==3:
        print ""+url
        VIDEOLINKS(url,name)




