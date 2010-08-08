import xbmcplugin
import xbmcgui
import xbmc

import common
import urllib,urllib2
import sys
import re
import os

pluginhandle = int (sys.argv[1])

class Main:

    def __init__( self ):
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        name = common.args.name
        showid = common.args.url
        if common.args.mode == 'List':
            self.VIDEOSHOWIDS(showid,name)
        elif common.args.mode == 'All':
            self.VIDEOLINKS(showid,name)
        elif common.args.mode == 'Latest':
            self.VIDEOLINKS(showid,name)
        elif common.args.mode == 'Popular':
            self.VIDEOLINKS(showid,name)
        elif common.args.mode == 'Editorial':
            self.VIDEOLINKS(showid,name)
        elif common.args.mode == 'Clips':
            self.VIDEOLINKS(showid,name)
        elif common.args.mode == 'Seasons':
            self.VIDEOLINKS(showid,name)        
        elif common.args.mode == 'SeasonsList':
            self.VIDEOSHOWSEASONS(showid,name)
        elif common.args.mode == 'ListHD':
            self.VIDEOLINKS(showid,name)
        elif common.args.mode == 'ListAny':
            self.VIDEOLINKS(showid,name)

    def VIDEOSHOWIDS(self,showid,name):
        if (xbmcplugin.getSetting(pluginhandle,'recent') == '0') or (xbmcplugin.getSetting(pluginhandle,'recent') == '1'):
            url = common.SITEFEED_URL + showid + "recent.js"
            if self.TESTURL(url) == True:
                    common.addDirectory(" Latest Videos",url,"Latest",common.args.thumbnail,common.args.thumbnail)
        if (xbmcplugin.getSetting(pluginhandle,'popular') == '0') or (xbmcplugin.getSetting(pluginhandle,'recent') == '1'):
            url = common.SITEFEED_URL + showid + "popular.js"
            if self.TESTURL(url) == True:
                    common.addDirectory(" Most Popular",url,"Popular",common.args.thumbnail,common.args.thumbnail)
        if (xbmcplugin.getSetting(pluginhandle,'editorial') == 'true'):
            url = common.SITEFEED_URL + showid + "editorial.js"
            if self.TESTURL(url) == True:
                    common.addDirectory(" Editor's Picks",url,"Editorial",common.args.thumbnail,common.args.thumbnail)
        if (xbmcplugin.getSetting(pluginhandle,'clips') == 'true'):
            url = common.SITEFEED_URL + showid + "clips.js"
            if self.TESTURL(url) == True:
                    common.addDirectory(" Clips",url,"Clips",common.args.thumbnail,common.args.thumbnail)
        if (xbmcplugin.getSetting(pluginhandle,'all') == 'true'):
            url = common.SITEFEED_URL + showid + "all.js"
            if self.TESTURL(url) == True:
                    common.addDirectory(" All Videos",url,"All",common.args.thumbnail,common.args.thumbnail)

        #Special Crimetime case. Normal video lists unavailable
        if showid == "/crimetime/":
                url = "http://www.cbs.com/crimetime/js/video/behind_the_scenes.js"
                if self.TESTURL(url) == True:
                    common.addDirectory("Behind the Scenes",url,"ListAny",common.args.thumbnail,common.args.thumbnail)
                url = "http://www.cbs.com/crimetime/js/video/48_hours.js"
                if self.TESTURL(url) == True:
                    common.addDirectory("48 Hours: Crimetime",url,"ListAny",common.args.thumbnail,common.args.thumbnail)
                
        #Full Episodes Listings
        url = common.SITEFEED_URL + showid + "episodes.js"
        #Check seasons.js for Season Count
        if self.CHECKSEASONS(showid) > 1:
                common.addDirectory(" Seasons",showid,"SeasonsList",common.args.thumbnail,common.args.thumbnail)
        #Add Episodes
        else:
                if self.TESTURL(url) == True:
                        self.VIDEOLINKS(url,name)
                        
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )


    def VIDEOSHOWSEASONS(self,showid,name):
        #Season Filter
        seasons = self.CHECKSEASONS(showid)
        C = 0
        for season in range(1,20):
                url = common.SITEFEED_URL + showid + str(season) + ".js"
                if self.TESTURL(url) == True:
                        C = C + 1
                        common.addDirectory('Season ' + str(season),url,'Seasons',common.args.thumbnail,common.args.thumbnail)
                        if C == int(seasons):
                            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
                            return
        url = url = "http://www.cbs.com/sitefeeds" + showid + "episodes.js"
        common.addDirectory('All Episodes',url,'ListAny',common.args.thumbnail,common.args.thumbnail)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
        


    #Tests URLs for errors 
    def TESTURL(self, url):
        link=common.getHTML(url)
        if link == False:
                return False
        else:
                #CHECKSEASONS
                if "seasons.js" in url:
                        return True
                #Check for a Video count other then 0
                match=re.compile('var videoCount = (.+?);').findall(link)
                videocount = match[0]
                if videocount == '0':
                        return False
                #This is a good Video list
                return True

            
    def CHECKSEASONS(self, showid):
        #Seasons
        url = "http://www.cbs.com/sitefeeds" + showid + "seasons.js"
        if self.TESTURL(url) == True:
                link=common.getHTML(url)
                match=re.compile('var categoryCount = (.+?);').findall(link)
                seasons = int(match[0])
                return seasons


    def VIDEOLINKS(self,url,name):
        showfilter = ''
        CLIPSDIR = False
        if url == "EpisodesClips":
            url = "Episodes"
            CLIPSDIR = True        
        if url == "Episodes":
            HD = True
            typefilter = url
            showfilter = name.replace(' Clips','')
            url = common.HDVIDEOS_URL
        elif url == "Clips":
            HD = True
            typefilter = url
            showfilter = name.replace(' Clips','')
            url = common.HDVIDEOS_URL
        else:
            typefilter = ''
            showfilter = ''
            HD = False

        hdcachefile = xbmc.translatePath(os.path.join(common.cachepath,"hd.js"))
        if url == common.HDVIDEOS_URL and os.path.isfile(hdcachefile):
            f = open(hdcachefile , 'r')
            link = f.read()
            f.close()
        else:
            link=common.getHTML(url)
        match=re.compile('videoProperties(.+?);\r').findall(link)
        #set List Counter to 1 for popular and recent shows
        if "popular" in url or "recent" in url or "editorial" in url :
                C = 1
        else:
                C = 0
        for url in match:
                # breakurl item list
                #  0 = empty
                #  1 = title1
                #  2 = title2
                #  3 = series_title
                #  4 = season_number
                #  5 = description
                #  6 = episode_number
                #  7 = primary_cid
                #  8 = category_type
                #  9 = runtime
                # 10 = pid or 480p pid
                # 11 = thumbnail 160x120
                # 12 = fullsize thumbnail 640x480
                # 13 = the current category value for the existing show pages(mostly blank)
                # 14 = site name in xml, lowercased and trimmed to match the value passed from the left menu(mostly blank)
                # 15 = empty or 720p pid
                breakurl = url.split("','")
                
                #480p, 720p, 1080p pids
                try:
                    breakurl[15] = breakurl[15].replace("')","")
                    breakurl[16] = breakurl[16].replace("')","")
                    pid = breakurl[10] + "<break>" + breakurl[15] + "<break>" + breakurl[16]
                #Standard Definition pid
                except:
                    breakurl[15] = breakurl[15].replace("')","")
                    if breakurl[15] == '':
                        pid = breakurl[10]
                        if HD == True:
                            continue
                if (xbmcplugin.getSetting(pluginhandle,'largethumbs') == 'true'):
                    thumbnail = breakurl[12]
                elif (xbmcplugin.getSetting(pluginhandle,'largethumbs') == 'false'):
                    thumbnail = breakurl[11]
                plot = breakurl[5].replace('\\','')
                duration = breakurl[9]
                #change single digit season numbers to 2 digits
                if len(breakurl[4]) == 1:
                        breakurl[4] = "0" + breakurl[4]
                #change single digit episode numbers to 2 digits
                if len(breakurl[6]) == 1:
                        breakurl[6] = "0" + breakurl[6]
                if breakurl[4] <> '':
                        try:
                            season = int(breakurl[4].replace('_','').replace('-','').replace('.',''))
                        except:
                            season = 0
                else:
                        season = 0
                if breakurl[6] <> '':
                        episode = int(breakurl[6].replace('_','').replace('-','').replace('.','').replace('A','').replace('T','')[-2])
                else:
                        episode = 0
                #seriestitle = breakurl[3]
                #episodetitle = breakurl[2]
                #List Order Counter for popular and recent lists
                if C <> 0:
                        if len(str(C)) == 1:
                                ordernumber = "#0" + str(C) + ". "                          
                        else:
                                ordernumber = "#" +str(C) + ". "
                        C = C + 1
                #Blank ordernumber value for all other lists
                else:
                        ordernumber = ''
                #Generate filename for Full Episode - series title + "S" + season number+ "E" + episode number + " - " + episode title
                if breakurl[8] == "Full Episode":
                         if "late" in breakurl[1] or "daytime" in breakurl[1]:
                                finalname = ordernumber + breakurl[2]
                         else:
                                finalname = ordernumber + "S" + breakurl[4] + "E" + breakurl[6] + " - " + breakurl[2]
                #Generate filename for Clip - series title + " - " + episode title + " (Clip)"
                elif breakurl[8] == "Clip": 
                        #finalname = ordernumber + breakurl[3] + " - " + breakurl[2] + " (Clip) " + breakurl[9]
                        if breakurl[2] == '':
                                finalname = ordernumber + breakurl[3] + " (Clip)"
                        if breakurl[3] in breakurl[2]:
                                finalname = ordernumber + breakurl[2] + " (Clip)"
                        else:
                                finalname = ordernumber + breakurl[2] + " (Clip)" 
                #HD title and for everything else
                else:
                        if len(breakurl[9]) > 4:
                            print breakurl
                            finalname = breakurl[3] + " E" + breakurl[6] + " - " + breakurl[2] # + " (" + breakurl[9] + ")"
                        elif len(breakurl[9]) <= 4:
                            if breakurl[3] in breakurl[2]:
                                finalname = breakurl[2] + " (Clip)" # (" + breakurl[9] + ")"
                            else:
                                finalname = breakurl[3] + " - " + breakurl[2] + " (Clip)" # + " (" + breakurl[9] + ")"
                #Clean filename
                finalname = finalname.replace('\\\'','\'')
                if "<break>" in pid:
                    if breakurl[3] == showfilter:
                        if typefilter == "Episodes":
                            if len(breakurl[9]) > 4:
                                passname = finalname.replace(ordernumber,'')
                                url = sys.argv[0]+'?mode="'+'Play'+'"&name="'+urllib.quote_plus(common.cleanNames(passname))+'"&pid="'+urllib.quote_plus(pid)+'"&thumbnail="'+urllib.quote_plus(common.cleanNames(thumbnail))+'"'#+'"&plot="'+urllib.quote_plus(plot)+'?duration="'+urllib.quote_plus(duration)+'?season="'+urllib.quote_plus(str(season))+'?episode="'+urllib.quote_plus(str(episode))+'"'
                                item=xbmcgui.ListItem(finalname, iconImage=thumbnail, thumbnailImage=thumbnail)
                                item.setInfo( type="Video",
                                             infoLabels={ "Title": finalname,
                                                            "Season": season,
                                                            "Episode": episode,
                                                            "Duration": duration,
                                                            "Plot": plot})
                                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True)
                                continue
                        elif typefilter == "Clips":
                            if len(breakurl[9]) <= 4:
                                passname = finalname.replace(ordernumber,'')
                                url = sys.argv[0]+'?mode="'+'Play'+'"&name="'+urllib.quote_plus(common.cleanNames(passname))+'"&pid="'+urllib.quote_plus(pid)+'"&thumbnail="'+urllib.quote_plus(common.cleanNames(thumbnail))+'"'#+'"&plot="'+urllib.quote_plus(plot)+'?duration="'+urllib.quote_plus(duration)+'?season="'+urllib.quote_plus(str(season))+'?episode="'+urllib.quote_plus(str(episode))+'"'
                                item=xbmcgui.ListItem(finalname, iconImage=thumbnail, thumbnailImage=thumbnail)
                                item.setInfo( type="Video",
                                            infoLabels={ "Title": finalname,
                                                            "Season": season,
                                                            "Episode": episode,
                                                            "Duration": duration,
                                                            "Plot": plot})
                                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True)
                                continue
                else:
                    passname = finalname.replace(ordernumber,'')
                    url = sys.argv[0]+'?mode="'+'Play'+'"&name="'+urllib.quote_plus(common.cleanNames(passname))+'"&pid="'+urllib.quote_plus(pid)+'"&thumbnail="'+urllib.quote_plus(common.cleanNames(thumbnail))+'"'#+'"&plot="'+urllib.quote_plus(plot)+'?duration="'+urllib.quote_plus(duration)+'?season="'+urllib.quote_plus(str(season))+'?episode="'+urllib.quote_plus(str(episode))+'"'
                    item=xbmcgui.ListItem(finalname, iconImage=thumbnail, thumbnailImage=thumbnail)
                    item.setInfo( type="Video",
                                 infoLabels={ "Title": finalname,
                                                "Season": season,
                                                "Episode": episode,
                                                "Duration": duration,
                                                "Plot": plot})
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item)
                    continue
        #add Clips Dir for HD
        if CLIPSDIR == True:
            common.addDirectory(showfilter +" Clips", "Clips", "ListHD")
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
                        
