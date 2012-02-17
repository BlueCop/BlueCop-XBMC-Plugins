#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmcplugin
import xbmc
import xbmcgui
import os.path
import sys
import urllib
import string
import shutil
import md5
import base64
import resources.lib.common as common

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup , Tag, NavigableString

try:
    from xml.etree import ElementTree
except:
    from elementtree import ElementTree

pluginhandle = common.handle

if (common.settings['enablelibraryfolder'] == 'true'):
    MOVIE_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.hulu/'),'Movies')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.hulu/'),'TV')
elif (common.settings['customlibraryfolder'] <> ''):
    MOVIE_PATH = os.path.join(xbmc.translatePath(common.settings['customlibraryfolder']),'Movies')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath(common.settings['customlibraryfolder']),'TV')    
    

dp_id = 'hulu'
if (common.settings['enable_plus'] == 'false'):
    package_id = '1'
elif (common.settings['enable_plus'] == 'true'):
    package_id = '2'

class Main:

    def __init__( self ):
        if (common.settings['enablelibraryfolder'] == 'true'):
            self.SetupHuluLibrary()
        elif (common.settings['customlibraryfolder'] <> ''):
            self.CreateDirectory(MOVIE_PATH)
            self.CreateDirectory(TV_SHOWS_PATH) 
        else:
            return

        if common.args.mode.startswith('Clear'):
            dialog = xbmcgui.Dialog()
            if dialog.yesno('Clear Exported Items', 'Are you sure you want to delete all exported items?'):
                shutil.rmtree(MOVIE_PATH)
                shutil.rmtree(TV_SHOWS_PATH)
            return
        
        if common.args.mode.startswith('Force'):
            self.EnableNotifications = True
        else:
            self.EnableNotifications = False

        if common.args.mode.endswith('QueueLibrary'):
            self.GetQueue()
        elif common.args.mode.endswith('SubscriptionsLibrary'):
            self.GetSubscriptions()
        elif common.args.mode.endswith('PopularMoviesLibrary'):
            self.GetPopMovies()
        elif common.args.mode.endswith('PopularShowsLibrary'):
            self.GetPopShows()
        elif common.args.mode.endswith('PopularEpisodesLibrary'):
            self.GetPopEpisodes()     
        elif common.args.mode.endswith('FullShowsLibrary'):
            self.GetFullShows()
        elif common.args.mode.endswith('FullMoviesLibrary'):
            self.GetFullMovies()
            
        if (common.settings['updatelibrary'] == 'true'):
            self.UpdateLibrary()

    def UpdateLibrary(self):
        xbmc.executebuiltin("UpdateLibrary(video)")

    def Notification(self,heading,message,duration=15000):
        if self.EnableNotifications == True:
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
            
    def SaveFile(self, filename, data, dir):
        path = os.path.join(dir, filename)
        file = open(path,'w')
        file.write(data)
        file.close()

    def CreateDirectory(self, dir_path):
        dir_path = dir_path.strip()
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    def cleanfilename(self, name):    
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in name if c in valid_chars)

    def GetSubscriptions(self):
        url = 'http://m.hulu.com/menu/hd_user_subscriptions?dp_id=hulu&limit=2000&package_id='+package_id+'&user_id='+common.settings['usertoken']
        self.ExportShowList(url)
        self.Notification('Hulu Library','Exported Subscriptions')
            
    def GetQueue(self):
        url = 'http://m.hulu.com/menu/hd_user_queue?dp_id=hulu&limit=2000&package_id='+package_id+'&user_id='+common.settings['usertoken']
        self.ExportVideoList(url)
        self.Notification('Hulu Library','Exported Queue')

    def GetPopShows(self):
        url = 'http://m.hulu.com/menu/11693?dp_id=hulu&package_id='+package_id+'&limit=100&page=1'
        self.ExportShowList(url)
        self.Notification('Hulu Library','Exported Popular Shows')
        
    def GetPopEpisodes(self):
        url = 'http://m.hulu.com/menu/11695?dp_id=hulu&package_id='+package_id+'&limit=100&page=1'
        self.ExportVideoList(url)
        self.Notification('Hulu Library','Exported Popular Episodes')

    def GetPopMovies(self):
        url = 'http://m.hulu.com/menu/11697?dp_id=hulu&package_id='+package_id+'&limit=100&page=1'
        self.ExportShowList(url)
        self.Notification('Hulu Library','Exported Popular Movies')

    def GetFullShows(self):
        url = 'http://m.hulu.com/menu/11808?dp_id=hulu&package_id='+package_id+'&limit=2000&page=1'
        self.ExportShowList(url,delay=1500)
        self.Notification('Hulu Library','Exported Full Episodes')
        
    def GetFullMovies(self):
        url = 'http://m.hulu.com/menu/11854?dp_id=hulu&package_id='+package_id+'&limit=2000&page=1'
        self.ExportShowList(url)
        url = 'http://m.hulu.com/menu/11854?dp_id=hulu&package_id='+package_id+'&limit=2000&page=2'
        self.ExportShowList(url)
        self.Notification('Hulu Library','Exported Full Movies')
        
    def ExportVideoList(self,url):
        xml=common.getFEED(url)
        tree = ElementTree.XML(xml)
        items = tree.findall('item')        
        del tree
        for item in items:
            self.ExportVideo(item)

    def ExportShowList(self,url,delay=0):  
        xml=common.getFEED(url)
        tree = ElementTree.XML(xml)
        items = tree.findall('item')        
        del tree
        for item in items:
            self.ExportShowMovie(item)
            xbmc.sleep(delay)
            
    def ExportShowMovie(self, item):
        feature_films_count = item.find('data').findtext('feature_films_count').strip()
        full_episodes_count = item.find('data').findtext('full_episodes_count').strip()
        if feature_films_count == '1' or feature_films_count == 1:
            title = item.find('data').findtext('name')
            filename = self.cleanfilename(title)
            content_id = item.find('data').findtext('feature_film_content_id')
            video_id = item.find('data').findtext('feature_film_id')
            eid = self.cid2eid(content_id)
            strm = 'plugin://plugin.video.hulu/?mode="TV_play"'
            strm += '&url="'+urllib.quote_plus(content_id)+'"'
            strm += '&videoid="'+urllib.quote_plus(video_id)+'"'
            strm += '&eid="'+urllib.quote_plus(eid)+'"'
            self.SaveFile( filename+'.strm', strm, MOVIE_PATH)
        elif full_episodes_count <> '':
            self.ExportShow(item)
        elif feature_films_count <> '':
            self.ExportShow(item)

    def cid2eid(self, content_id):
        m = md5.new()
        m.update(str(content_id) + "MAZxpK3WwazfARjIpSXKQ9cmg9nPe5wIOOfKuBIfz7bNdat6gQKHj69ZWNWNVB1")
        value = m.digest()
        return base64.encodestring(value).replace("+", "-").replace("/", "_").replace("=", "").replace('\n','')
    
    def ExportShow(self, show):
        data = show.find('data')
        #show_name = data.findtext('name')
        #directory = os.path.join(TV_SHOWS_PATH,self.cleanfilename(show_name))
        #self.CreateDirectory(directory)
        show_id = data.findtext('show_id')
        url = 'http://m.hulu.com/menu/11674?show_id='+show_id+'&dp_id=hulu&limit=2000&package_id='+package_id
        xml=common.getFEED(url)
        tree = ElementTree.XML(xml)
        episodes = tree.findall('item')        
        del tree
        for episode in episodes:
            self.ExportVideo(episode)
        #self.Notification('Added Subscription',show_name)

    def ExportVideo(self, episode):
        data = episode.find('data')
        if data:
            content_id = data.findtext('content_id')
            video_id = data.findtext('video_id')
            eid = data.findtext('eid')
            strm = 'plugin://plugin.video.hulu/?mode="TV_play"'
            strm += '&url="'+urllib.quote_plus(content_id)+'"'
            strm += '&videoid="'+urllib.quote_plus(video_id)+'"'
            strm += '&eid="'+urllib.quote_plus(eid)+'"'
            media_type = data.findtext('media_type')
            if media_type == 'TV' or media_type == 'Web Original':
                title = data.findtext('title').encode('utf-8').strip()
                season = data.findtext('season_number').encode('utf-8')
                episode = data.findtext('episode_number').encode('utf-8')
                show_name = data.findtext('show_name').encode('utf-8').strip()
                filename = self.cleanfilename('S%sE%s - %s' % (season,episode,title))
                directory = os.path.join(TV_SHOWS_PATH,self.cleanfilename(show_name))
                self.CreateDirectory(directory)
                self.SaveFile( filename+'.strm', strm, directory)
                if common.settings['episodenfo'] == 'true':
                    episodeDetails  = '<episodedetails>'
                    episodeDetails += '<title>'+title+' '+common.settings['librarysuffix']+'</title>'
                    try:rating = str(float(data.findtext('rating'))*2)
                    except:rating = ''
                    episodeDetails += '<rating>'+rating+'</rating>'
                    episodeDetails += '<season>'+season+'</season>'
                    episodeDetails += '<episode>'+episode+'</episode>'
                    expires_at = data.findtext('expires_at')
                    description = unicode(data.findtext('description').replace('\n', ' ').replace('\r', ' ')).encode('utf-8')
                    if data.findtext('plus_only') == 'True': plot = description
                    else:
                        if expires_at: plot = 'Expires: '+expires_at.encode('utf-8')+'\n'+description
                        else: plot = description
                    episodeDetails += '<plot>'+plot+'</plot>'
                    episodeDetails += '<thumb>'+data.findtext('thumbnail_url_16x9_large')+'</thumb>'
                    original_premiere = data.findtext('original_premiere_date').replace(' 00:00:00','')
                    year = original_premiere.split('-')[0]
                    episodeDetails += '<year>'+year+'</year>'
                    episodeDetails += '<aired>'+original_premiere+'</aired>'
                    episodeDetails += '<premiered>'+original_premiere+'</premiered>'
                    episodeDetails += '<studio>'+data.findtext('company_name')+'</studio>'
                    episodeDetails += '<mpaa>'+data.findtext('content_rating')+'</mpaa>'
                    ishd = data.findtext('has_hd')
                    hasSubtitles = data.findtext('has_captions')
                    language = data.findtext('language', default="").upper()
                    durationseconds = data.findtext('duration')
                    episodeDetails += self.streamDetails(durationseconds, ishd, language, hasSubtitles)
                    episodeDetails += '</episodedetails>'
                    self.SaveFile( filename+'.nfo', episodeDetails, directory)
            elif media_type == 'Film':
                title = data.findtext('title').encode('utf-8')
                filename = self.cleanfilename(title)
                #directory = os.path.join(MOVIE_PATH,self.cleanfilename(title))
                #self.CreateDirectory(directory)
                directory = MOVIE_PATH
                self.SaveFile( filename+'.strm', strm, directory)
                if common.settings['movienfo'] == 'true':
                    movie = '<movie>'
                    movie += '<title>'+title+' '+common.settings['librarysuffix']+'</title>'
                    try:rating = str(float(data.findtext('rating'))*2)
                    except:rating = ''
                    movie += '<rating>'+rating+'</rating>'
                    expires_at = data.findtext('expires_at')
                    description = unicode(data.findtext('description').replace('\n', ' ').replace('\r', ' ')).encode('utf-8')
                    if data.findtext('plus_only') == 'True': plot = description
                    else:
                        if expires_at: plot = 'Expires: '+expires_at.encode('utf-8')+'\n'+description
                        else: plot = description
                    movie += '<plot>'+plot+'</plot>'
                    movie += '<thumb>'+data.findtext('thumbnail_url_16x9_large')+'</thumb>'
                    original_premiere = data.findtext('original_premiere_date').replace(' 00:00:00','')
                    year = original_premiere.split('-')[0]
                    movie += '<year>'+year+'</year>'
                    movie += '<aired>'+original_premiere+'</aired>'
                    movie += '<premiered>'+original_premiere+'</premiered>'
                    movie += '<studio>'+data.findtext('company_name')+'</studio>'
                    movie += '<mpaa>'+data.findtext('content_rating')+'</mpaa>'
                    ishd = data.findtext('has_hd')
                    hasSubtitles = data.findtext('has_captions')
                    language = data.findtext('language', default="").upper()
                    durationseconds = data.findtext('duration')
                    movie += self.streamDetails(durationseconds, ishd, language, hasSubtitles)
                    movie += '</movie>'
                    self.SaveFile(filename+'.nfo', movie, directory)

    def streamDetails(self, duration, ishd, language, hasSubtitles):      
        fileinfo  = '<fileinfo>'
        fileinfo += '<streamdetails>'
        fileinfo += '<audio>'
        fileinfo += '<channels>2</channels>'
        fileinfo += '<codec>aac</codec>'
        fileinfo += '</audio>'
        fileinfo += '<video>'
        fileinfo += '<codec>h264</codec>'
        fileinfo += '<durationinseconds>'+duration+'</durationinseconds>'
        if ishd == 'true':
            fileinfo += '<aspect>1.778</aspect>'
            fileinfo += '<height>720</height>'
            fileinfo += '<width>1280</width>'
        else:
            fileinfo += '<height>400</height>'
            fileinfo += '<width>720</width>'        
        fileinfo += '<language>'+language+'</language>'
        #fileinfo += '<longlanguage>English</longlanguage>'
        fileinfo += '<scantype>Progressive</scantype>'
        fileinfo += '</video>'
        if hasSubtitles == 'true':
            fileinfo += '<subtitle>'
            fileinfo += '<language>eng</language>'
            fileinfo += '</subtitle>'
        fileinfo += '</streamdetails>'
        fileinfo += '</fileinfo>'
        return fileinfo

    def SetupHuluLibrary(self):
        print "Trying to add Hulu source paths..."
        source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
        dialog = xbmcgui.Dialog()
        
        self.CreateDirectory(MOVIE_PATH)
        self.CreateDirectory(TV_SHOWS_PATH)
        
        try:
            file = open(source_path, 'r')
            contents=file.read()
            file.close()
        except:
            dialog.ok("Error","Could not read from sources.xml, does it really exist?")
            file = open(source_path, 'w')
            content = "<sources>\n"
            content += "    <programs>"
            content += "        <default pathversion=\"1\"></default>"
            content += "    </programs>"
            content += "    <video>"
            content += "        <default pathversion=\"1\"></default>"
            content += "    </video>"
            content += "    <music>"
            content += "        <default pathversion=\"1\"></default>"
            content += "    </music>"
            content += "    <pictures>"
            content += "        <default pathversion=\"1\"></default>"
            content += "    </pictures>"
            content += "    <files>"
            content += "        <default pathversion=\"1\"></default>"
            content += "    </files>"
            content += "</sources>"
            file.close()
    
        soup = BeautifulSoup(contents)  
        video = soup.find("video")      
            
        if len(soup.findAll(text="Hulu Movies")) < 1:
            movie_source_tag = Tag(soup, "source")
            movie_name_tag = Tag(soup, "name")
            movie_name_tag.insert(0, "Hulu Movies")
            movie_path_tag = Tag(soup, "path")
            movie_path_tag['pathversion'] = 1
            movie_path_tag.insert(0, MOVIE_PATH)
            movie_source_tag.insert(0, movie_name_tag)
            movie_source_tag.insert(1, movie_path_tag)
            video.insert(2, movie_source_tag)
    
        if len(soup.findAll(text="Hulu Subscriptions")) < 1: 
            tvshow_source_tag = Tag(soup, "source")
            tvshow_name_tag = Tag(soup, "name")
            tvshow_name_tag.insert(0, "Hulu Subscriptions")
            tvshow_path_tag = Tag(soup, "path")
            tvshow_path_tag['pathversion'] = 1
            tvshow_path_tag.insert(0, TV_SHOWS_PATH)
            tvshow_source_tag.insert(0, tvshow_name_tag)
            tvshow_source_tag.insert(1, tvshow_path_tag)
            video.insert(2, tvshow_source_tag)
        
        
        string = ""
        for i in soup:
            string = string + str(i)
        
        file = open(source_path, 'w')
        file.write(str(soup))
        file.close()
        print "Source paths added!"
