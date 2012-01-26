#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmcplugin
import xbmc
import xbmcgui
import os.path
import sys
import urllib
import string
import resources.lib.common as common

from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup , Tag, NavigableString

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
        if common.args.mode == 'updatexbmclibrary':
            self.GetQueue()
        else:
            self.GetSubscriptions()
            
        if (common.settings['updatelibrary'] == 'true'):
            self.UpdateLibrary()

    def UpdateLibrary(self):
        xbmc.executebuiltin("UpdateLibrary(video)")

    def Notification(self,heading,message,duration=10000):
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
       
    def createElement(self, tagname,contents):
        soup = BeautifulSoup()
        element = Tag(soup, tagname)
        text = NavigableString(contents)
        element.insert(0, text)
        return element
    
    def cleanfilename(self, name):    
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in name if c in valid_chars)
    
    def GetQueue(self, NFO=True):
        url = 'http://m.hulu.com/menu/hd_user_queue?dp_id=hulu&cb=201102070846&limit=2000&package_id='+package_id+'&user_id='+common.settings['usertoken']
        self.Notification('Hulu Library','Queue Update',duration=15000)
        episodes = self.GetEpisodesData(url)
        for content_id,video_id,media_type,show_name,episodetitle,season,episode,premiered,year,duration,plot,studio, mpaa,rating,votes,thumb,fanart,ishd,expires_at in episodes:
            #self.Notification('Added Video',episodetitle)
            episodetitle = episodetitle.replace(':','').replace('/',' ').strip()
            u = 'plugin://plugin.video.hulu/'
            u += '?mode="TV_play"'
            u += '&url="'+urllib.quote_plus(content_id)+'"'
            u += '&videoid="'+urllib.quote_plus(video_id)+'"'
            if media_type == 'TV':
                filename = self.cleanfilename('S%sE%s - %s' % (season,episode,episodetitle))
                directory = os.path.join(TV_SHOWS_PATH,self.cleanfilename(show_name))
                self.CreateDirectory(directory)
                self.SaveFile( filename+'.strm', u, directory)
            elif media_type == 'Film':
                filename = self.cleanfilename(episodetitle)
                self.SaveFile( filename+'.strm', u, MOVIE_PATH)
            if NFO:
                soup = BeautifulStoneSoup()
                if media_type == 'Film':
                    movie = Tag(soup, "movie")
                    soup.insert(0, movie)
                    movie.insert(0, self.createElement('title',episodetitle+' (Hulu)'))
                    if expires_at:
                        plot = 'Expires: '+expires_at.encode('utf-8')+'\n'+plot
                    movie.insert(1, self.createElement('plot',plot))
                    movie.insert(2, self.createElement('aired',premiered))
                    movie.insert(3, self.createElement('premiered',premiered))
                    movie.insert(4, self.createElement('year',str(year)))
                    movie.insert(5, self.createElement('studio',studio))
                    movie.insert(6, self.createElement('mpaa',mpaa))
                    movie.insert(7, self.createElement('thumb',thumb))
                    movie.insert(8, self.createElement('rating',str(rating)))
                    fileinfo = self.createElement('fileinfo','')
                    streamdetails = self.createElement('streamdetails','')
                    audio = self.createElement('audio','')
                    audio.insert(0, self.createElement('channels','2'))
                    audio.insert(1, self.createElement('codec','aac'))
                    streamdetails.insert(0,audio)
                    video = self.createElement('video','')
                    video.insert(0, self.createElement('codec','h264'))
                    if ishd == 'true' or ishd == 'True':
                        video.insert(1, self.createElement('height','720'))
                        video.insert(2, self.createElement('width','1280'))
                        video.insert(3, self.createElement('aspect','1.778'))
                    else:
                        video.insert(1, self.createElement('height','400'))
                        video.insert(2, self.createElement('width','720'))
                    video.insert(4, self.createElement('durationinseconds',duration))
                    video.insert(5, self.createElement('scantype','Progressive'))
                    streamdetails.insert(1,video)
                    fileinfo.insert(0,streamdetails)
                    movie.insert(9, fileinfo)
                    self.SaveFile( filename+'.nfo', str(soup), MOVIE_PATH)
                elif media_type == 'TV':
                    episodedetails = Tag(soup, "episodedetails")
                    soup.insert(0, episodedetails)
                    episodedetails.insert(0, self.createElement('title',episodetitle+' (Hulu)'))
                    episodedetails.insert(1, self.createElement('season',str(season)))
                    episodedetails.insert(2, self.createElement('episode',str(episode)))
                    if expires_at:
                        plot = 'Expires: '+expires_at.encode('utf-8')+'\n'+plot
                    episodedetails.insert(3, self.createElement('plot',plot))
                    episodedetails.insert(4, self.createElement('aired',premiered))
                    episodedetails.insert(5, self.createElement('premiered',premiered))
                    episodedetails.insert(6, self.createElement('year',str(year)))
                    episodedetails.insert(7, self.createElement('studio',studio))
                    episodedetails.insert(8, self.createElement('mpaa',mpaa))
                    episodedetails.insert(9, self.createElement('thumb',thumb))
                    episodedetails.insert(10, self.createElement('rating',str(rating)))
                    fileinfo = self.createElement('fileinfo','')
                    streamdetails = self.createElement('streamdetails','')
                    audio = self.createElement('audio','')
                    audio.insert(0, self.createElement('channels','2'))
                    audio.insert(1, self.createElement('codec','aac'))
                    streamdetails.insert(0,audio)
                    video = self.createElement('video','')
                    video.insert(0, self.createElement('codec','h264'))
                    if ishd == 'true' or ishd == 'True':
                        video.insert(1, self.createElement('height','720'))
                        video.insert(2, self.createElement('width','1280'))
                        video.insert(3, self.createElement('aspect','1.778'))
                    else:
                        video.insert(1, self.createElement('height','400'))
                        video.insert(2, self.createElement('width','720'))
                    video.insert(4, self.createElement('durationinseconds',duration))
                    video.insert(5, self.createElement('scantype','Progressive'))
                    streamdetails.insert(1,video)
                    fileinfo.insert(0,streamdetails)
                    episodedetails.insert(11, fileinfo)
                    self.SaveFile( filename+'.nfo', str(soup), directory)
            
    def GetSubscriptions(self, NFO=False):
        url = 'http://m.hulu.com/menu/hd_user_subscriptions?dp_id=hulu&cb=201102070846&limit=2000&package_id='+package_id+'&user_id='+common.settings['usertoken']
        self.Notification('Hulu Library','Subscriptions Update',duration=15000)
        shows = self.GetSubscriptionsData(url)
        for show_name,art,genre,plot,stars,network,premiered,year,show_id in shows:
            self.Notification('Added Subscription',show_name)
            directory = os.path.join(TV_SHOWS_PATH,self.cleanfilename(show_name))
            self.CreateDirectory(directory)
            if NFO:
                soup = BeautifulStoneSoup()
                tvshow = Tag(soup, "tvshow")
                soup.insert(0, tvshow)
                tvshow.insert(0, self.createElement('title',show_name))
                if year:
                    tvshow.insert(1, self.createElement('year',str(year)))
                if plot:
                    tvshow.insert(2, self.createElement('plot',plot))
                if stars:
                    tvshow.insert(4, self.createElement('rating',str(stars)))
                if network:
                    tvshow.insert(5, self.createElement('studio',network))
                if art:
                    fanart_tag = self.createElement('fanart','')
                    fanart_tag['url'] = 'http://assets.hulu.com/shows/' 
                    fanart_tag.insert(0, self.createElement('thumb',art.replace('http://assets.hulu.com/shows/','')))
                    tvshow.insert(6,fanart_tag)
                    tvshow.insert(7, self.createElement('thumb',art))
                if genre:
                    tvshow.insert(8, self.createElement('genre',genre))
                self.SaveFile( 'tvshow.nfo', str(soup), directory)
            self.GetEpisodes( directory, show_id)
        
    def GetSubscriptionsData(self, url):
        data=common.getFEED(url)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        subscriptions=tree.findAll('item')
        returnshows = []
        for show in subscriptions:
            seriestitle=show('display')[0].string.encode('utf-8')
            #url='http://m.hulu.com'+show('items_url')[0].string+'dp_id='+dp_id+'&package_id='+package_id+'&limit=2000&page=1'
            mode=show('app_data')[0]('cmtype')[0].string
            data = show('data')
            if data:
                data = data[0]
                canonical_name = data('canonical_name')[0].string
                show_name = data('name')[0].string.encode('utf-8')
                genre_data = data('genre')
                if genre_data:
                    genre = genre_data[0].string
                art = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                description_data = data('description')
                if description_data:
                    if description_data[0].string:
                        description = unicode(common.cleanNames(description_data[0].string.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
                    else:
                        description = ''
                else:
                    description = ''
                rating_data = data('rating')
                if rating_data:
                    if rating_data[0].string:
                        rating = float(rating_data[0].string)*2
                premiered_data = data('original_premiere_date')
                if premiered_data[0].string:
                    premiered = premiered_data[0].string.replace(' 00:00:00','')
                    year = int(premiered.split('-')[0])
                company_name_data = data('company_name')
                if company_name_data:
                    company_name = company_name_data[0].string
                ishd_data = data('has_hd')
                if ishd_data:
                    ishd = ishd_data[0].string
                show_id_data = data('show_id')
                if show_id_data:
                    show_id = show_id_data[0].string
            returnshows.append([show_name,art,genre,description,rating,company_name,premiered,year,show_id])     
        return returnshows
    
    def GetEpisodes(self, directory, showid, NFO=True):
        url = 'http://m.hulu.com/menu/11674?show_id='+showid+'&dp_id=hulu&limit=2000&package_id='+package_id
        episodes = self.GetEpisodesData(url)
        for content_id,video_id,media_type,showname,episodetitle,season,episode,premiered,year,duration,plot,studio, mpaa,rating,votes,thumb,fanart,ishd,expires_at in episodes:
            episodetitle = episodetitle.replace(':','').replace('/',' ').strip()
            filename = self.cleanfilename('S%sE%s - %s' % (season,episode,episodetitle))
            u = 'plugin://plugin.video.hulu/'
            u += '?mode="TV_play"'
            u += '&url="'+urllib.quote_plus(content_id)+'"'
            u += '&videoid="'+urllib.quote_plus(video_id)+'"'
            self.SaveFile( filename+".strm", u, directory)
            if NFO:
                soup = BeautifulStoneSoup()
                episodedetails = Tag(soup, "episodedetails")
                soup.insert(0, episodedetails)
                episodedetails.insert(0, self.createElement('title',episodetitle+' (Hulu)'))
                if season:
                    episodedetails.insert(1, self.createElement('season',str(season)))
                if episode:
                    episodedetails.insert(2, self.createElement('episode',str(episode)))
                if plot:
                    if expires_at:
                        plot = 'Expires: '+expires_at.encode('utf-8')+'\n'+plot
                    episodedetails.insert(3, self.createElement('plot',plot))
                if premiered:
                    episodedetails.insert(4, self.createElement('aired',premiered))
                    episodedetails.insert(5, self.createElement('premiered',premiered))
                if year:
                    episodedetails.insert(6, self.createElement('year',str(year)))
                if studio:
                    episodedetails.insert(7, self.createElement('studio',studio))
                if mpaa:
                    episodedetails.insert(8, self.createElement('mpaa',mpaa))
                if thumb:
                    episodedetails.insert(9, self.createElement('thumb',thumb))
                if rating:
                    episodedetails.insert(10, self.createElement('rating',str(rating)))
                fileinfo = self.createElement('fileinfo','')
                streamdetails = self.createElement('streamdetails','')
                audio = self.createElement('audio','')
                audio.insert(0, self.createElement('channels','2'))
                audio.insert(1, self.createElement('codec','aac'))
                streamdetails.insert(0,audio)
                video = self.createElement('video','')
                video.insert(0, self.createElement('codec','h264'))
                if ishd == 'true' or ishd == 'True':
                    video.insert(1, self.createElement('height','720'))
                    video.insert(2, self.createElement('width','1280'))
                    video.insert(3, self.createElement('aspect','1.778'))
                else:
                    video.insert(1, self.createElement('height','400'))
                    video.insert(2, self.createElement('width','720'))
                video.insert(4, self.createElement('durationinseconds',duration))
                video.insert(5, self.createElement('scantype','Progressive'))
                streamdetails.insert(1,video)
                fileinfo.insert(0,streamdetails)
                episodedetails.insert(11, fileinfo)
                self.SaveFile( filename+'.nfo', str(soup), directory)

    def GetEpisodesData(self, url):
        data=common.getFEED(url)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        episodes=tree.findAll('item')
        returnepisodes = []
        for episode in episodes:
            episodetitle=episode('display')[0].string.encode('utf-8')
            url='http://m.hulu.com'+episode('items_url')[0].string
            mode=episode('app_data')[0]('cmtype')[0].string
            data = episode('data')
            if data:
                data = data[0]
                canonical_name = data('show_canonical_name')[0].string
                if canonical_name:
                    fanart = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                else:
                    fanart = False
                content_id = data('content_id')[0].string
                media_type = data('media_type')[0].string
                video_id = data('video_id')[0].string
                if media_type == 'TV' or media_type == 'Web Original':
                    show_name = data('show_name')[0].string.encode('utf-8')
                    season_number = data('season_number')[0].string.encode('utf-8')
                    episode_number = data('episode_number')[0].string.encode('utf-8')                   
                elif media_type == 'Film':
                    show_name = ''
                    season_number = ''
                    episode_number = ''
                thumb = data('thumbnail_url_16x9_large')[0].string
                mpaa = data('content_rating')[0].string
                votes = data('votes_count')[0].string
                try:
                    premiered = data('original_premiere_date')[0].string.replace(' 00:00:00','')
                    year = int(premiered.split('-')[0])
                except:
                    premiered = ''
                    year = ''
                duration = data('duration')[0].string
                description = data('description')[0].string
                description = unicode(common.cleanNames(description.replace('\n', ' ').replace('\r', ' '))).encode('utf-8')
                try:
                    rating = str(float(data('rating')[0].string)*2)
                except:
                    rating = ''
                company_name = data('company_name')[0].string
                expires_at = data('expires_at')[0].string
                ishd = data('has_hd')[0].string
                #art = "http://assets.hulu.com/shows/key_art_"+canonical_name.replace('-','_')+".jpg"
                returnepisodes.append([content_id,
                                       video_id,
                                       media_type,
                                       show_name,
                                       episodetitle,
                                       season_number,
                                       episode_number,
                                       premiered,
                                       year,
                                       duration,
                                       description,
                                       company_name,
                                       mpaa,
                                       rating,
                                       votes,
                                       thumb,
                                       fanart,
                                       ishd,
                                       expires_at])
        return returnepisodes
    
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
