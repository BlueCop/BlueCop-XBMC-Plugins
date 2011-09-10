#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import os.path
import re
import urllib
import xbmcplugin
import xbmc
import xbmcgui
import resources.lib.common as common
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite
    
TV_URL = 'http://www.amazon.com/gp/search/ref=sr_st?qid=1314982661&rh=n%3A2625373011%2Cn%3A!2644981011%2Cn%3A!2644982011%2Cn%3A2858778011%2Cn%3A2864549011%2Cp_85%3A2470955011&sort=-releasedate'

################################ TV db

def createTVdb():
    c = tvDB.cursor()
    c.execute('''CREATE TABLE shows(
                 seriestitle TEXT,
                 plot TEXT,
                 creator TEXT,
                 network TEXT,
                 genres TEXT,
                 actors TEXT,
                 year INTEGER,
                 stars float,
                 votes TEXT,
                 episodetotal INTEGER,
                 watched INTEGER,
                 unwatched INTEGER,
                 isHD BOOLEAN,
                 isprime BOOLEAN,
                 favor BOOLEAN,
                 TVDBbanner TEXT,
                 TVDBposter TEXT,
                 TVDBfanart TEXT,
                 TVDB_ID TEXT,
                 PRIMARY KEY(seriestitle)
                 );''')
    c.execute('''CREATE TABLE seasons(
                 url TEXT,
                 poster TEXT,
                 season INTEGER,
                 seriestitle TEXT,
                 plot TEXT,
                 creator TEXT,
                 network TEXT,
                 genres TEXT,
                 actors TEXT,
                 year INTEGER,
                 stars float,
                 votes TEXT,
                 episodetotal INTEGER,
                 watched INTEGER,
                 unwatched INTEGER,
                 isHD BOOLEAN,
                 isprime BOOLEAN,
                 PRIMARY KEY(seriestitle,season,isHD),
                 FOREIGN KEY(seriestitle) REFERENCES shows(seriestitle)
                 );''')
    c.execute('''create table episodes(
                 asin TEXT,
                 seriestitle TEXT,
                 season INTEGER,
                 episode INTEGER,
                 episodetitle TEXT,
                 url TEXT,
                 plot TEXT,
                 airdate TEXT,
                 runtime TEXT,
                 isHD BOOLEAN,
                 isprime BOOLEAN,
                 watched BOOLEAN,
                 PRIMARY KEY(seriestitle,season,episode,episodetitle),
                 FOREIGN KEY(seriestitle,season) REFERENCES seasons(seriestitle,season)
                 );''')
    tvDB.commit()
    c.close()

def loadTVShowdb(HDonly=False,genrefilter=False,creatorfilter=False,networkfilter=False,yearfilter=False,watchedfilter=False,favorfilter=False,isprime=True):
    c = tvDB.cursor()
    if HDonly:
        return c.execute('select distinct * from shows where isprime = (?) and isHD = (?)', (isprime,HDonly))
    elif genrefilter:
        genrefilter = '%'+genrefilter+'%'
        return c.execute('select distinct * from shows where isprime = (?) and genres like (?)', (isprime,genrefilter))
    elif creatorfilter:
        return c.execute('select distinct * from shows where isprime = (?) and creator = (?)', (isprime,creatorfilter))
    elif networkfilter:
        return c.execute('select distinct * from shows where isprime = (?) and network = (?)', (isprime,networkfilter))
    elif yearfilter:    
        return c.execute('select distinct * from shows where isprime = (?) and year = (?)', (isprime,int(yearfilter)))
    elif favorfilter:
        return c.execute('select distinct * from shows where isprime = (?) and favor = (?)', (isprime,favorfilter)) 
    else:
        return c.execute('select distinct * from shows where isprime = (?)', (isprime,))

def loadTVSeasonsdb(showname,HDonly=False,isprime=True):
    c = tvDB.cursor()
    if HDonly:
        return c.execute('select distinct * from seasons where isprime = (?) and (seriestitle = (?) and isHD = (?))', (isprime,showname,HDonly))
    else:
        return c.execute('select distinct * from seasons where isprime = (?) and seriestitle = (?)', (isprime,showname))

def loadTVEpisodesdb(showname,season,HDonly=False,isprime=True):
    c = tvDB.cursor()
    if HDonly:
        return c.execute('select distinct * from episodes where isprime = (?) and (seriestitle = (?) and season = (?) and isHD = (?)) order by episode', (isprime,showname,season,HDonly))
    else:
        return c.execute('select distinct * from episodes where isprime = (?) and (seriestitle = (?) and season = (?) and isHD = (?)) order by episode', (isprime,showname,season,HDonly))

def getShowTypes(col):
    c = tvDB.cursor()
    items = c.execute('select distinct %s from seasons' % col)
    list = []
    for data in items:
        if data and data[0] <> None:
            data = data[0]
            if type(data) == type(str()):
                data = data.decode('utf-8').encode('utf-8').split(',')
                for item in data:
                    item = item.replace('& ','').strip()
                    if item not in list and item <> ' Inc':
                        list.append(item)
            else:
                list.append(str(data))
    c.close()
    return list

def getPoster(seriestitle):
    c = tvDB.cursor()
    data = c.execute('select distinct poster from seasons where seriestitle = (?)', (seriestitle,)).fetchone()
    return data[0]

def fixHDshows():
    c = tvDB.cursor()
    HDseasons = c.execute('select distinct seriestitle from seasons where isHD = (?)', (True,)).fetchall()
    for series in HDseasons:
        c.execute("update shows set isHD=? where seriestitle=?", (True,series[0]))
    tvDB.commit()
    c.close()
    
def fixGenres():
    c = tvDB.cursor()
    seasons = c.execute('select distinct seriestitle,genres from seasons where genres is not null').fetchall()
    for series,genres in seasons:
        c.execute("update seasons set genres=? where seriestitle=? and genres is null", (genres,series))
        c.execute("update shows set genres=? where seriestitle=? and genres is null", (genres,series))
    tvDB.commit()
    c.close()
    
def fixYears():
    c = tvDB.cursor()
    seasons = c.execute('select seriestitle,year from seasons where year is not null order by year desc').fetchall()
    for series,year in seasons:
        c.execute("update shows set year=? where seriestitle=?", (year,series))
    tvDB.commit()
    c.close()
    
def deleteShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = common.args.title
    c = tvDB.cursor()
    c.execute('delete from shows where seriestitle = (?)', (seriestitle,))
    c.execute('delete from seasons where seriestitle = (?)', (seriestitle,))
    tvDB.commit()
    c.close()

def renameShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = common.args.title
    keyb = xbmc.Keyboard(seriestitle, 'Show Rename')
    keyb.doModal()
    if (keyb.isConfirmed()):
            newname = keyb.getText()
            c = tvDB.cursor()
            c.execute("update or replace shows set seriestitle=? where seriestitle=?", (newname,seriestitle))
            c.execute("update seasons set seriestitle=? where seriestitle=?", (newname,seriestitle))
            c.execute("update episodes set seriestitle=? where seriestitle=?", (newname,seriestitle))
            tvDB.commit()
            c.close()

def deleteSeasondb(seriestitle=False,season=False):
    if not seriestitle and not season:
        seriestitle = common.args.title
        season = int(common.args.season)
    c = tvDB.cursor()
    c.execute('delete from seasons where seriestitle = (?) and season = (?)', (seriestitle,season))
    c.execute('delete from episodes where seriestitle = (?) and season = (?)', (seriestitle,season))
    tvDB.commit()
    c.close()

def renameSeasondb(seriestitle=False,season=False):
    if not seriestitle and not season:
        seriestitle = common.args.title
        season = int(common.args.season)
    keyb = xbmc.Keyboard(seriestitle, 'Season Rename')
    keyb.doModal()
    if (keyb.isConfirmed()):
            newname = keyb.getText()
            c = tvDB.cursor()
            c.execute("update or ignore seasons set seriestitle=? where seriestitle=? and season = ?", (newname,seriestitle,season))
            c.execute("update or ignore episodes set seriestitle=? where seriestitle=? and season = ?", (newname,seriestitle,season))
            tvDB.commit()
            c.close()

def favorShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = common.args.title
    c = tvDB.cursor()
    c.execute("update shows set favor=? where seriestitle=?", (True,seriestitle))
    tvDB.commit()
    c.close()
    
def unfavorShowdb(seriestitle=False):
    if not seriestitle:
        seriestitle = common.args.title
    c = tvDB.cursor()
    c.execute("update shows set favor=? where seriestitle=?", (False,seriestitle))
    tvDB.commit()
    c.close()
    
def watchEpisodedb(asin=False):
    if not asin:
        asin = common.args.url
    c = tvDB.cursor()
    c.execute("update episodes set watched=? where asin=?", (True,asin))
    tvDB.commit()
    c.close()
    
def unwatchEpisodedb(asin=False):
    if not asin:
        asin = common.args.url
    c = tvDB.cursor()
    c.execute("update episodes set watched=? where asin=?", (False,asin))
    tvDB.commit()
    c.close()

def addEpisodedb(episodedata):
    print 'AMAZON: addEpisodedb'
    print episodedata
    c = tvDB.cursor()
    c.execute('insert or ignore into episodes values (?,?,?,?,?,?,?,?,?,?,?,?)', episodedata)
    tvDB.commit()
    c.close()
    
def addSeasondb(seasondata):
    print 'AMAZON: addSeasondb'
    print seasondata
    c = tvDB.cursor()
    c.execute('insert or ignore into seasons values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', seasondata)
    tvDB.commit()
    c.close()

def addShowdb(showdata):
    print 'AMAZON: addShowdb'
    print showdata
    seriestitle = showdata[0]
    #seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart
    c = tvDB.cursor()
    c.execute('insert or ignore into shows values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', showdata)
    tvDB.commit()
    c.close()

def addTVdb(url=TV_URL,isprime=True):
    dialog = xbmcgui.DialogProgress()
    dialog.create('Building Prime TV Database')
    dialog.update(0,'Initializing TV Scan')
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    total = int(tree.find('div',attrs={'id':'resultCount','class':'resultCount'}).span.string.replace(',','').split('of')[1].split('Results')[0].strip())
    del tree; del data
    pages = (total/12)+1
    increment = 100.0 / pages 
    page = 1
    percent = int(increment*page)
    dialog.update(percent,'Scanning Page %s or %s' % (str(page),str(pages)))
    pagenext = scrapeTVdb(url,isprime)
    while pagenext:
        pagenext = scrapeTVdb(pagenext,isprime)
        page += 1
        percent = int(increment*page)
        dialog.update(percent,'Scanning Page %s or %s' % (str(page),str(pages)))
        pagenext = scrapeMoviesdb(pagenext,isprime)
        if (dialog.iscanceled()):
            return False
    fixHDshows()
    fixGenres()
    fixYears()
    
def scrapeTVdb(url,isprime):
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    atf = tree.find(attrs={'id':'atfResults'}).findAll('div',recursive=False)
    try:
        btf = tree.find(attrs={'id':'btfResults'}).findAll('div',recursive=False)
        atf.extend(btf)
        del btf
    except:
        print 'AMAZON: No btf found'
    nextpage = tree.find(attrs={'title':'Next page','id':'pagnNextLink','class':'pagnNext'})
    del tree
    del data
    for show in atf:
        showasin = show['name']
        url = common.BASE_URL+'/gp/product/'+showasin
        name = show.find('a', attrs={'class':'title'}).string
        poster = show.find(attrs={'class':'image'}).find('img')['src'].replace('._AA160_','')
        if '[HD]' in name: isHD = True
        else: isHD = False
        seriestitle = name.split('Season ')[0].split('season ')[0].split('Volume ')[0].split('Series ')[0].split('Year ')[0].split(' The Complete')[0].replace('[HD]','').strip().strip('-').strip(',').strip(':').strip()
        if seriestitle.endswith('-') or seriestitle.endswith(',') or seriestitle.endswith(':'):
            seriestitle = name[:-1].strip()
        try:
            if 'Season' in name:
                seasonGuess = int(name.split('Season')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'Volume' in name:
                seasonGuess = int(name.split('Volume')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'Series' in name:
                seasonGuess = int(name.split('Series')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'Year' in name:
                seasonGuess = int(name.split('Year')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            elif 'season' in name:
                seasonGuess = int(name.split('season')[1].replace('[HD]','').strip('-').strip(',').strip(':').strip())
            else:
                seasonGuess = False
        except:
            seasonGuess = False
        if seasonGuess:
            strseason = str(seasonGuess)
            if len(strseason)>2 and strseason in name:
                seriesnamecheck = seriestitle.replace(strseason,'').strip()
            else:
                seriesnamecheck = seriestitle
            seasondata = checkSeasonInfo(seriesnamecheck,seasonGuess,isHD)
            if seasondata:
                print 'AMAZON: Returning Cached Meta for SEASON: '+str(seasonGuess)+' SERIES: '+seriestitle
                print seasondata
                continue
        showdata, episodes = scrapeShowInfo(url,owned=False)
        season,episodetotal,plot,creator,runtime,year,network,actors,genres,stars,votes = showdata
        strseason = str(season)
        if len(strseason)>2 and strseason in name:
            seriestitle = seriestitle.replace(strseason,'').strip()
        seasondata = checkSeasonInfo(seriestitle,season,isHD)
        if seasondata:
            print 'AMAZON: Returning Cached Meta for SEASON: '+str(season)+' SERIES: '+seriestitle
            print seasondata
            continue
        #          seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime,favor,TVDBbanner,TVDBposter,TVDBfanart
        addShowdb([seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,0,episodetotal,isHD,isprime,False,None,None,None,None])
        for episodeASIN,Eseason,episodeNum,episodetitle,eurl,eplot,eairDate,eisHD in episodes:
            #                    asin,seriestitle,season,episode,episodetitle,url,plot,airdate,runtime,isHD,isprime,watched
            addEpisodedb([episodeASIN,seriestitle,Eseason,episodeNum,episodetitle,eurl,eplot,eairDate,runtime,eisHD,isprime,False])
        #            url,poster,season,seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,watched,unwatched,isHD,isprime
        addSeasondb([url,poster,season,seriestitle,plot,creator,network,genres,actors,year,stars,votes,episodetotal,0,episodetotal,isHD,isprime])
    del atf
    if nextpage:
        pagenext = common.BASE_URL + nextpage['href']
        del nextpage
        return pagenext
    else:
        return False

def checkSeasonInfo(seriestitle,season,isHD):
    c = tvDB.cursor()
    metadata = c.execute('select * from seasons where seriestitle = (?) and season = (?) and isHD = (?)', (seriestitle,season,isHD))
    returndata = metadata.fetchone()
    c.close()
    return returndata

def scrapeShowInfo(url,owned=False):
    tags = re.compile(r'<.*?>')
    scripts = re.compile(r'<script.*?script>',re.DOTALL)
    spaces = re.compile(r'\s+')
    data = common.getURL(url)
    tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    try:season = int(tree.find('div',attrs={'class':'unbox_season_selected'}).string)
    except:
        try:season = int(tree.find('div',attrs={'style':'font-size: 120%;font-weight:bold; margin-top:15px;margin-bottom:10px;'}).contents[0].split('Season')[1].strip())
        except:season = None
    episodes = []
    try:
        episodebox = tree.find('div',attrs={'id':'avod-ep-list-rows'}).findAll('tr',attrs={'asin':True})
        episodecount = len(episodebox)
        for episode in episodebox:
            if owned:
                purchasecheckbox = episode.find('input',attrs={'type':'checkbox'})
                if purchasecheckbox:
                    continue
            episodeASIN = episode['asin']
            episodetitle = episode.find(attrs={'title':True})['title'].encode('utf-8')
            if '[HD]' in episodetitle:
                episodetitle.replace('[HD]','').strip()
                isHD = True
            else:
                isHD = False
            airDate = episode.find(attrs={'style':'width: 150px; overflow: hidden'}).string.strip()
            try: plot =  episode.findAll('div')[1].string.strip()
            except: plot = ''
            episodeNum = int(episode.find('div',attrs={'style':'width: 185px;'}).string.split('.')[0].strip())
            url = common.BASE_URL+'/gp/product/'+episodeASIN
            episodedata = [episodeASIN,season,episodeNum,episodetitle,url,plot,airDate,isHD]
            episodes.append(episodedata)
        del episodebox
    except:
        episodecount = None
    try:
        stardata = tree.find('span',attrs={'class':'crAvgStars'}).renderContents()
        stardata = scripts.sub('', stardata)
        stardata = tags.sub('', stardata)
        stardata = spaces.sub(' ', stardata).strip().split('out of ')
        stars = float(stardata[0])*2
        votes = stardata[1].split('customer reviews')[0].split('See all reviews')[1].replace('(','').strip()
    except:
        stars = None
        votes = None
    metadatas = tree.findAll('div', attrs={'style':'margin-top:7px;margin-bottom:7px;'})
    del tree, data
    metadict = {}
    for metadata in metadatas:
        mdata = metadata.renderContents()
        mdata = scripts.sub('', mdata)
        mdata = tags.sub('', mdata)
        mdata = spaces.sub(' ', mdata).strip().split(': ')
        fd = ''
        for md in mdata[1:]:
            fd += md+' '
        metadict[mdata[0].strip()] = fd.strip()
    try:plot = metadict['Synopsis']
    except: plot = None
    try:creator = metadict['Creator']
    except:creator = None
    try:
        runtime = metadict['Runtime']
        if 'hours' in runtime:
            split = 'hours'
        elif 'hour' in runtime:
            split = 'hour'
        if 'minutes' in runtime:
            replace = 'minutes'
        elif 'minute' in runtime:
            replace = 'minute'
        if 'hour' not in runtime:
            runtime = runtime.replace(replace,'')
            minutes = int(runtime.strip())
        elif 'minute' not in runtime:
            runtime = runtime.replace(split,'')
            minutes = (int(runtime.strip())*60)     
        else:
            runtime = runtime.replace(replace,'').split(split)
            try:
                minutes = (int(runtime[0].strip())*60)+int(runtime[1].strip())
            except:
                minutes = (int(runtime[0].strip())*60)
        runtime = str(minutes)
    except: runtime = None
    try: year = int(metadict['Season year'])
    except: year = None
    try: network = metadict['Network']
    except: network = None
    try: actors = metadict['Starring']+', '+metadict['Supporting actors']
    except:
        try: actors = metadict['Starring']
        except: actors = None     
    try: genres = metadict['Genre']
    except: genres = None
    showdata = [season,episodecount,plot,creator,runtime,year,network,actors,genres,stars,votes]
    return showdata, episodes


def refreshTVDBshow(seriestitle=False):
    if not seriestitle:
        seriestitle = common.args.title
    c = tvDB.cursor()
    seriestitle,genre,year,TVDB_ID = c.execute('select distinct seriestitle,genres,year,TVDB_ID from shows where seriestitle = ?', (seriestitle,)).fetchone()
    #for seriestitle,genre,year,TVDB_ID in show:
    TVDBbanner,TVDBposter,TVDBfanart,genre2,year2,seriesid = tv_db_id_lookup(TVDB_ID,seriestitle)
    if not genre:
        genre = genre2
    if not year:
        try:
            year = int(year2.split('-')[0])
        except:
            year = None
    c.execute("update shows set TVDBbanner=?,TVDBposter=?,TVDBfanart=?,TVDB_ID=?,genres=?,year=? where seriestitle=?", (TVDBbanner,TVDBposter,TVDBfanart,seriesid,genre,year,seriestitle))
    tvDB.commit()

def scanTVDBshow(seriestitle=False):
    if not seriestitle:
        seriestitle = common.args.title
    c = tvDB.cursor()
    seriestitle,genre,year,TVDB_ID = c.execute('select distinct seriestitle,genres,year,TVDB_ID from shows where seriestitle = ?', (seriestitle,)).fetchone()
    #for seriestitle,genre,year,TVDB_ID in show:
    TVDBbanner,TVDBposter,TVDBfanart,genre2,year2,seriesid = tv_db_series_lookup(seriestitle,manualsearch=True)
    if not genre:
        genre = genre2
    if not year:
        try:
            year = int(year2.split('-')[0])
        except:
            year = None
    c.execute("update shows set TVDBbanner=?,TVDBposter=?,TVDBfanart=?,TVDB_ID=?,genres=?,year=? where seriestitle=?", (TVDBbanner,TVDBposter,TVDBfanart,seriesid,genre,year,seriestitle))
    tvDB.commit()

def scanTVDBshows():
    c = tvDB.cursor()
    shows = c.execute('select distinct seriestitle,genres,year from shows order by seriestitle').fetchall()
    dialog = xbmcgui.DialogProgress()
    dialog.create('Refreshing Prime TV Database')
    dialog.update(0,'Scanning TVDB Data')
    #len(shows)
    for seriestitle,genre,year in shows:
        TVDBbanner,TVDBposter,TVDBfanart,genre2,year2,seriesid = tv_db_series_lookup(seriestitle)
        if not genre:
            genre = genre2
        if not year:
            try:
                year = int(year2.split('-')[0])
            except:
                year = None
        c.execute("update shows set TVDBbanner=?,TVDBposter=?,TVDBfanart=?,TVDB_ID=?,genres=?,year=? where seriestitle=?", (TVDBbanner,TVDBposter,TVDBfanart,seriesid,genre,year,seriestitle))
        tvDB.commit()
        if (dialog.iscanceled()):
            return False
    c.close()


def tv_db_series_lookup(seriesname,manualsearch=False):
    tv_api_key = '03B8C17597ECBD64'
    mirror = 'http://thetvdb.com'
    banners = 'http://thetvdb.com/banners/'
    try:
        print 'intial search'
        series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname)
        seriesid = common.getURL(series_lookup)
        seriesid = get_series_id(seriesid,seriesname)
    except:
        try:
            print 'strip search'
            series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(seriesname.split('(')[0].split(':')[0].strip())
            seriesid = common.getURL(series_lookup)
            seriesid = get_series_id(seriesid,seriesname)
        except:
            #return None,None,None,None
            if manualsearch:
                print 'manual search'
                keyb = xbmc.Keyboard(seriesname, 'Manual Search')
                keyb.doModal()
                if (keyb.isConfirmed()):
                    try:
                        series_lookup = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='+urllib.quote_plus(keyb.getText())
                        seriesid = common.getURL(series_lookup)
                        seriesid = get_series_id(seriesid,seriesname)
                    except:
                        print 'manual search failed'
                        return None,None,None,None,None,None
            else:
                return None,None,None,None,None,None
    if seriesid:
        return tv_db_id_lookup(seriesid,seriesname)
  
def tv_db_id_lookup(seriesid,seriesname):
    tv_api_key = '03B8C17597ECBD64'
    mirror = 'http://thetvdb.com'
    banners = 'http://thetvdb.com/banners/'
    if seriesid:
        series_xml = mirror+('/api/%s/series/%s/en.xml' % (tv_api_key, seriesid))
        series_xml = common.getURL(series_xml)
        tree = BeautifulStoneSoup(series_xml, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        try:
            genre = tree.find('genre').string
            genre = genre.replace("|",",")
            genre = genre.strip(",")
        except:
            print '%s - Genre Failed' % seriesname
            genre = None
        try: aired = tree.find('firstaired').string
        except:
            print '%s - Air Date Failed' % seriesname
            aired = None
        try: banner = banners + tree.find('banner').string
        except:
            print '%s - Banner Failed' % seriesname
            banner = None
        try: fanart = banners + tree.find('fanart').string
        except:
            print '%s - Fanart Failed' % seriesname
            fanart = None
        try: poster = banners + tree.find('poster').string
        except:
            print '%s - Poster Failed' % seriesname
            poster = None
        return banner, poster, fanart, genre, aired, seriesid
    else:
        return None,None,None,None,None,None

def get_series_id(seriesid,seriesname):
    shows = BeautifulStoneSoup(seriesid, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('series')
    names = list(BeautifulStoneSoup(seriesid, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll('seriesname'))
    if len(names) > 1:
        select = xbmcgui.Dialog()
        ret = select.select(seriesname, [name.string for name in names])
        if ret <> -1:
            seriesid = shows[ret].find('seriesid').string
        else:
            seriesid = False
    else:
        seriesid = shows[0].find('seriesid').string
    return seriesid

tvDBfile = os.path.join(xbmc.translatePath(common.pluginpath),'resources','cache','tv.db')
tvDByourfile = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.amazon/'),'tv.db')
if not os.path.exists(tvDByourfile) and os.path.exists(tvDBfile):
    import shutil
    shutil.copyfile(tvDBfile, tvDByourfile)
    tvDB = sqlite.connect(tvDByourfile)
    tvDB.text_factory = str
elif not os.path.exists(tvDByourfile):
    tvDB = sqlite.connect(tvDByourfile)
    tvDB.text_factory = str
    createTVdb()
else:
    tvDB = sqlite.connect(tvDByourfile)
    tvDB.text_factory = str