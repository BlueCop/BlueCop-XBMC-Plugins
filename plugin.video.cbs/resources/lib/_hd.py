import xbmcplugin
import xbmcgui
import xbmc

import common
import urllib,urllib2
import sys
import re
import os

class Main:

    def __init__( self ):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        if common.args.mode == 'HD':
            url = common.HDVIDEOS_URL
            self.HDSHOWS(url)

    def HDSHOWS(self,url):
        link=common.getHTML(url)
        hdcachefile = xbmc.translatePath(os.path.join(common.cachepath,"hd.js"))
        f = open(hdcachefile , 'w')
        plot = f.write(str(link))
        f.close()
        match=re.compile('videoProperties(.+?);\r').findall(link)
        SHOWLIST = ['']
        CLIPLIST = ['']
        EPISODELIST = ['']
        #set List Counter to 1 for popular and recent shows
        for url in match:
                breakurl = url.split("','")
                SHOWNAME = breakurl[3]
                if SHOWNAME <> '':
                    Episodes = False
                    Clips = False
                    if len(breakurl[9]) > 4:
                        Episodes = True
                    if len(breakurl[9]) <= 4:
                        Clips = True
                    if SHOWLIST[0] == '':
                        #print "first run"
                        SHOWLIST[0] = SHOWNAME
                        EPISODELIST[0] = Episodes
                        CLIPLIST[0] = Clips
                    elif SHOWNAME in SHOWLIST:
                        #print "existing show"
                        i = SHOWLIST.index(SHOWNAME)
                        if Episodes == True:
                            EPISODELIST[i] = Episodes 
                        elif Clips == True:
                            CLIPLIST[i] = Clips
                    else:
                        #print "New Show"
                        SHOWLIST.append(SHOWNAME)
                        EPISODELIST.append(Episodes)
                        CLIPLIST.append(Clips)
                else:
                    print "NO SHOW NAME: " + breakurl 

        #for SHOWNAME,Episodes,Clips in SHOWLIST:
        for SHOWNAME in SHOWLIST:
            i = SHOWLIST.index(SHOWNAME)
            Episodes = EPISODELIST[i]
            Clips = CLIPLIST[i]
            if Episodes == True and Clips == True:
                common.addDirectory(SHOWNAME, 'EpisodesClips', 'ListHD')
            elif Episodes == True:
                common.addDirectory(SHOWNAME, 'Episodes', 'ListHD')
            elif Clips == True:
                common.addDirectory(SHOWNAME, "Clips", "ListHD")
                
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ) )
