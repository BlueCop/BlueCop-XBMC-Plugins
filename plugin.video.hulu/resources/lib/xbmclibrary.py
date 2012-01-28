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

pluginhandle = common.pluginhandle

if (common.addon.getSetting('enablelibraryfolder') == 'true'):
    MOVIE_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.amazon/'),'Movies')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.amazon/'),'TV')
elif (common.addon.getSetting('customlibraryfolder') <> ''):
    MOVIE_PATH = os.path.join(xbmc.translatePath(common.addon.getSetting('customlibraryfolder')),'Movies')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath(common.addon.getSetting('customlibraryfolder')),'TV') 

def UpdateLibrary():
    xbmc.executebuiltin("UpdateLibrary(video)") 

def CreateStreamFile(name, url, dir):
    try:
        u = 'plugin://plugin.video.amazon/'
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="play"'
        u += '&sitemode="PLAYVIDEO"'
        filename = name + ".strm"
        path = os.path.join(dir, filename)
        file = open(path,'w')
        file.write(u)
        file.close()
    except:
        print "Error while creating strm file for : " + name

def cleanfilename(name):    
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)	

def createElement(tagname,contents):
    soup = BeautifulSoup()
    element = Tag(soup, tagname)
    text = NavigableString(contents)
    element.insert(0, text)
    return element

def LIST_MOVIES():
    if (common.addon.getSetting('enablelibraryfolder') == 'true'):
        SetupAmazonLibrary()
    elif (common.addon.getSetting('customlibraryfolder') <> ''):
        CreateDirectory(MOVIE_PATH)
        CreateDirectory(TV_SHOWS_PATH)   
    import movies as moviesDB
    movies = moviesDB.loadMoviedb(favorfilter=True)
    for asin,movietitle,url,poster,plot,director,writer,runtime,year,premiered,studio,mpaa,actors,genres,stars,votes,TMDBbanner,TMDBposter,TMDBfanart,isprime,watched,favor,TMDB_ID in movies:
        CreateStreamFile(movietitle, url, MOVIE_PATH)
        soup = BeautifulSoup()
        movie = Tag(soup, "movie")
        soup.insert(0, movie)
        movie.insert(0, createElement('title',movietitle+' (Amazon)'))
        if year:
            movie.insert(1, createElement('year',str(year)))
        if premiered:
            movie.insert(1, createElement('premiered',premiered))
        if plot:
            movie.insert(2, createElement('plot',plot))
        if runtime:
            movie.insert(2, createElement('runtime',runtime))
        if votes:
            movie.insert(3, createElement('votes',str(votes)))
        if stars:
            movie.insert(4, createElement('rating',str(stars)))
        if director:
            movie.insert(5, createElement('director',director))
        if studio:
            movie.insert(6, createElement('studio',studio))       
        if poster:
            movie.insert(7, createElement('thumb',poster))
        if mpaa:
            movie.insert(8, createElement('mpaa',mpaa)) 
        u  = sys.argv[0]
        u += '?url="'+urllib.quote_plus(url)+'"'
        u += '&mode="play"'
        u += '&name="'+urllib.quote_plus(movietitle)+'"'
        utrailer = u+'&sitemode="PLAYTRAILER"'    
        movie.insert(9, createElement('trailer',utrailer))
        fileinfo = createElement('fileinfo','')
        streamdetails = createElement('streamdetails','')
        audio = createElement('audio','')
        audio.insert(0, createElement('channels','2'))
        audio.insert(1, createElement('codec','aac'))
        streamdetails.insert(0,audio)
        video = createElement('video','')
        video.insert(0, createElement('codec','h264'))
        video.insert(1, createElement('height','400'))
        video.insert(2, createElement('width','720'))
        video.insert(4, createElement('scantype','Progressive'))
        streamdetails.insert(1,video)
        fileinfo.insert(0,streamdetails)
        movie.insert(10, fileinfo)
        index = 10   
        if genres:
            for genre in genres.split(','):
                index += 1
                movie.insert(index, createElement('genre',genre))
        if actors:
            for actor in actors.split(','):
                if actor <> None:
                    index += 1
                    actortag = createElement('actor','')
                    actorname = createElement('name',actor)
                    actortag.insert(0,actorname)
                    movie.insert(index, actortag )
        movieNFO = os.path.join(MOVIE_PATH,movietitle+'.nfo')
        file = open(movieNFO, 'w')
        file.write(str(soup))
        file.close()
		
def LIST_TVSHOWS(NFO=False):
    import tv as tvDB
    shows = tvDB.loadTVShowdb(favorfilter=True)
    if (common.addon.getSetting('enablelibraryfolder') == 'true'):
        SetupAmazonLibrary()
    elif (common.addon.getSetting('customlibraryfolder') <> ''):
        CreateDirectory(MOVIE_PATH)
        CreateDirectory(TV_SHOWS_PATH)                          
    for seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart,TVDBseriesid in shows:
        directorname = os.path.join(TV_SHOWS_PATH,seriestitle.replace(':',''))
    	CreateDirectory(directorname)
        if NFO:
            soup = BeautifulStoneSoup()
            tvshow = Tag(soup, "tvshow")
            soup.insert(0, tvshow)
            tvshow.insert(0, createElement('title',seriestitle))
            if year:
                tvshow.insert(1, createElement('year',str(year)))
            if plot:
                tvshow.insert(2, createElement('plot',plot))
            if votes:
                tvshow.insert(3, createElement('votes',str(votes)))
            if stars:
                tvshow.insert(4, createElement('rating',str(stars)))
            if creator:
                tvshow.insert(5, createElement('credits',creator))
            if network:
                tvshow.insert(6, createElement('studio',network))
            if TVDBseriesid:
                tvshow.insert(7, createElement('id',TVDBseriesid))
                episodeguide = createElement('episodeguide','')
                url = createElement('url','http://www.thetvdb.com/api/03B8C17597ECBD64/series/'+TVDBseriesid+'/all/en.zip')
                url['cache'] = TVDBseriesid+'.xml'
                episodeguide.insert(0,url)
                tvshow.insert(8, episodeguide)
            if TVDBfanart:
                fanart_tag = createElement('fanart','')
                fanart_tag['url'] = 'http://thetvdb.com/banners/' 
                fanart_tag.insert(0,createElement('thumb',TVDBfanart.replace('http://thetvdb.com/banners/','')))
                tvshow.insert(9,fanart_tag)
            if TVDBposter:
                tvshow.insert(10,createElement('thumb',TVDBposter))
            elif TVDBbanner:
                tvshow.insert(11,createElement('thumb',TVDBbanner))
            index = 11
            if genres:
                for genre in genres.split(','):
                    index += 1
                    tvshow.insert(index, createElement('genre',genre))
            if actors:
                for actor in actors.split(','):
                    if actor <> None:
                        index += 1
                        actortag = createElement('actor','')
                        actorname = createElement('name',actor)
                        actortag.insert(0,actorname)
                        tvshow.insert(index, actortag )
        seasonTotal,episodeTotal,seasons = LIST_TV_SEASONS(seriestitle,isHD)
        for season,poster,hasHD in seasons:
            name = 'Season '+str(season)
            if hasHD:
                name += ' HD'
            seasonpath = os.path.join(directorname,name)
            CreateDirectory(seasonpath)
            if NFO:
                postertag = createElement('thumb',poster)
                postertag['type'] = 'season'
                postertag['season'] = str(season)
                index += 1
                tvshow.insert(index,postertag)
            LIST_EPISODES_DB(seriestitle,int(season),poster,HDonly=hasHD,path=seasonpath)
        if NFO:
            index += 1
            tvshow.insert(index, createElement('season',seasonTotal))
            index += 1
            tvshow.insert(index, createElement('episode',episodeTotal))  
            tvshowNFO = os.path.join(directorname,'tvshow.nfo')
            data = str(soup)
            if TVDBseriesid:
                data = 'http://thetvdb.com/index.php?tab=series&id='+TVDBseriesid
                file = open(tvshowNFO, 'w')
                file.write(data)
                file.close()
    #UpdateLibrary()
    
def LIST_TV_SEASONS(namefilter,HDonly=False):
    import tv as tvDB
    seasons = tvDB.loadTVSeasonsdb(showname=namefilter,HDonly=HDonly).fetchall()
    seasonTotal = len(seasons)
    seasonsreturn = []
    episodereturn = 0
    for url,poster,season,seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime in seasons:
        seasonsreturn.append([season,poster,isHD])
        if episodetotal:
            episodereturn += episodetotal
    return str(seasonTotal),str(episodereturn),seasonsreturn

def LIST_EPISODES_DB(seriestitle,season,poster,HDonly=False,path=False,NFO=True):
    import tv as tvDB
    episodes = tvDB.loadTVEpisodesdb(seriestitle,season,HDonly)
    #asin,seriestitle,season,episode,episodetitle,url,plot,airdate,runtime,isHD,isprime,watched
    for asin,seriestitle,season,episode,episodetitle,url,plot,airdate,runtime,isHD,isprime,watched in episodes:
        episodetitle = episodetitle.replace(':','').replace('/',' ').replace('[HD]','').strip()
        if seriestitle in episodetitle:
            episodetitle = episodetitle.replace(seriestitle,'').strip().strip(',').strip('')
        if 'Season ' in episodetitle:
            episodetitle = episodetitle.replace('Season ','S')
        filename = 'S%sE%s - %s' % (season,episode,cleanfilename(episodetitle))
    	CreateStreamFile(filename, url, path)
        if NFO:
            soup = BeautifulStoneSoup()
            episodedetails = Tag(soup, "episodedetails")
            soup.insert(0, episodedetails)
            episodedetails.insert(0, createElement('title',episodetitle+' (Amazon)'))
            if season:
                episodedetails.insert(1, createElement('season',str(season)))
            if episode:
                episodedetails.insert(2, createElement('episode',str(episode)))
            if plot:
                episodedetails.insert(3, createElement('plot',plot))
            if airdate:
                episodedetails.insert(4, createElement('aired',airdate))
                episodedetails.insert(5, createElement('premiered',airdate))
            episodedetails.insert(6, createElement('thumb',poster))
   
            fileinfo = createElement('fileinfo','')
            streamdetails = createElement('streamdetails','')
            audio = createElement('audio','')
            audio.insert(0, createElement('channels','2'))
            audio.insert(1, createElement('codec','aac'))
            streamdetails.insert(0,audio)
            video = createElement('video','')
            video.insert(0, createElement('codec','h264'))
            if isHD:
                video.insert(1, createElement('height','720'))
                video.insert(2, createElement('width','1280'))
                video.insert(3, createElement('aspect','1.778'))
            else:
                video.insert(1, createElement('height','480'))
                video.insert(2, createElement('width','640'))
            video.insert(3, createElement('scantype','Progressive'))
            streamdetails.insert(1,video)
            fileinfo.insert(0,streamdetails)
            episodedetails.insert(7, fileinfo)
                
            episodeNFO = os.path.join(path,filename+'.nfo')
            file = open(episodeNFO, 'w')
            file.write(str(soup))
            file.close()

def CreateDirectory(dir_path):
    dir_path = dir_path.strip()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def SetupAmazonLibrary():
    print "Trying to add Amazon source paths..."
    source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
    dialog = xbmcgui.Dialog()
    
    CreateDirectory(MOVIE_PATH)
    CreateDirectory(TV_SHOWS_PATH)
    
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
        
    if len(soup.findAll(text="Amazon Movies")) < 1:
        movie_source_tag = Tag(soup, "source")
        movie_name_tag = Tag(soup, "name")
        movie_name_tag.insert(0, "Amazon Movies")
        movie_path_tag = Tag(soup, "path")
        movie_path_tag['pathversion'] = 1
        movie_path_tag.insert(0, MOVIE_PATH)
        movie_source_tag.insert(0, movie_name_tag)
        movie_source_tag.insert(1, movie_path_tag)
        video.insert(2, movie_source_tag)

    if len(soup.findAll(text="Amazon TV")) < 1: 
        tvshow_source_tag = Tag(soup, "source")
        tvshow_name_tag = Tag(soup, "name")
        tvshow_name_tag.insert(0, "Amazon TV")
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
    
    #dialog = xbmcgui.Dialog()
    #dialog.ok("Source folders added", "To complete the setup:", " 1) Restart XBMC.", " 2) Set the content type of added folders.")
    #Appearently this restarted everything and not just XBMC... :(
    #if dialog.yesno("Restart now?", "Do you want to restart XBMC now?"):
    #   xbmc.restart()
