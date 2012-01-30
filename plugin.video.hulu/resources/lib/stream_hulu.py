import xbmc
import xbmcgui
import xbmcplugin

import common
import ads
import subtitles
import sys
import binascii
import base64
import os
import hmac
import operator
import time
import urllib
from array import array

from BeautifulSoup import BeautifulStoneSoup

try:
    from xml.etree import ElementTree
except:
    from elementtree import ElementTree


smildeckeys = [ common.xmldeckeys[9] ]

class Main:
    def __init__( self ):
        video_id=common.args.url
        admodule = ads.Main()
        common.playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        if common.args.mode.endswith('TV_play'):
            if os.path.isfile(common.ADCACHE):
                os.remove(common.ADCACHE)
            self.queue=False
            self.NoResolve=False
            self.GUID = common.makeGUID()
            
            if common.args.mode.startswith('Captions'):
                common.settings['enable_captions']='true'
                common.settings['segmentvideos'] = 'false'
                self.NoResolve=True
            elif common.args.mode.startswith('NoCaptions'):
                common.settings['enable_captions']='false'
                common.settings['segmentvideos'] = 'false'
                self.NoResolve=True
            elif common.args.mode.startswith('Select'):
                common.settings['quality']='0'
                common.settings['segmentvideos'] = 'false'
                self.NoResolve=True
            
            # POST VIEW
            if common.settings['enable_login']=='true' and common.settings['usertoken']:
                common.viewed(common.args.videoid)
                
            if not self.NoResolve:
                if (common.settings['networkpreroll'] == 'true'):
                    self.NetworkPreroll()
                addcount = admodule.PreRoll(video_id,self.GUID,self.queue)
                if addcount > 0:
                    self.queue=True
            else:
                addcount = 0
            if common.settings['segmentvideos'] == 'true':
                segments = self.playSegment(video_id)
                if segments:
                    adbreaks = common.settings['adbreaks']
                    for i in range(1,len(segments)+1):
                        admodule.queueAD(video_id,adbreaks+addcount,addcount)
                        addcount += adbreaks
                        self.queueVideoSegment(video_id,segment=i)
            else:
                self.play(video_id)
            admodule.Trailing(addcount,video_id,self.GUID)
            
            if common.settings['enable_login']=='true' and common.settings['usertoken']:
                self.queueViewComplete()
                
        elif common.args.mode == 'SEGMENT_play':
            self.queue=False
            self.NoResolve=False
            self.GUID = common.args.guid
            self.playSegment(video_id,segment=int(common.args.segment))
        elif common.args.mode == 'AD_play':
            self.NoResolve=False
            self.GUID = common.args.guid
            pod = int(common.args.pod)
            admodule.playAD(video_id,pod,self.GUID)
        elif common.args.mode == 'SUBTITLE_play':
            subtitles.Main().SetSubtitles(video_id)
              
    def getSMIL(self, video_id,retry=0):
        epoch = int(time.mktime(time.gmtime()))
        parameters = {'video_id'  : video_id,
                      'v'         : '888324234',
                      'ts'        : str(epoch),
                      'np'        : '1',
                      'vp'        : '1',
                      'device_id' : self.GUID,
                      'pp'        : 'Desktop',
                      'dp_id'     : 'Hulu',
                      'region'    : 'US',
                      'ep'        : '1',
                      'language'  : 'en'
                      }
        if retry > 0:
            parameters['retry']=str(retry)
        if common.settings['enable_login']=='true' and common.settings['enable_plus']=='true' and common.settings['usertoken']:
            parameters['token'] = common.settings['usertoken']
        smilURL = False
        for item1, item2 in parameters.iteritems():
            if not smilURL:
                smilURL = 'http://s.hulu.com/select?'+item1+'='+item2
            else:
                smilURL += '&'+item1+'='+item2
        smilURL += '&bcs='+self.content_sig(parameters)
        print 'HULU --> SMILURL: ' + smilURL
        if common.settings['proxy_enable'] == 'true':
            proxy=True
        else:
            proxy=False
        smilXML=common.getFEED(smilURL,proxy=proxy)
        if smilXML:
            smilXML=self.decrypt_SMIL(smilXML)
            print "GOT SMIL"
            if smilXML:
                smilSoup=BeautifulStoneSoup(smilXML, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
                print smilSoup.prettify()
                return smilSoup
            else:
                return False
        else:
            return False
        
    def content_sig(self, parameters):
        hmac_key = 'f6daaa397d51f568dd068709b0ce8e93293e078f7dfc3b40dd8c32d36d2b3ce1'
        sorted_parameters = sorted(parameters.iteritems(), key=operator.itemgetter(0))
        data = ''
        for item1, item2 in sorted_parameters:
            data += item1 + item2
        sig = hmac.new(hmac_key, data)
        return sig.hexdigest()

    def decrypt_SMIL(self, encsmil):
        encdata = binascii.unhexlify(encsmil)
        expire_message = 'Your access to play this content has expired.'
        plus_message = 'please close any Hulu Plus videos you may be watching on other devices'
        for key in smildeckeys[:]:
            cbc = common.AES_CBC(binascii.unhexlify(key[0]))
            smil = cbc.decrypt(encdata,key[1])
            
            print smil
            if (smil.find("<smil") == 0):
                #print key
                i = smil.rfind("</smil>")
                smil = smil[0:i+7]
                return smil
            elif expire_message in smil:
                xbmcgui.Dialog().ok('Content Expired',expire_message)
                return False
            elif plus_message in smil:
                xbmcgui.Dialog().ok('Too many connections',plus_message)
                return False
    
    def queueViewComplete(self):
        u = sys.argv[0]
        u += "?mode='viewcomplete'"
        u += '&videoid="'+urllib.quote_plus(common.args.videoid)+'"'
        item=xbmcgui.ListItem("Remove from Queue")
        common.playlist.add(url=u, listitem=item)

    def queueVideoSegment( self, video_id, segment=False):
        mode='SEGMENT_play'
        u = sys.argv[0]
        u += '?url="'+urllib.quote_plus(video_id)+'"'
        u += '&mode="'+urllib.quote_plus(mode)+'"'
        u += '&videoid="'+urllib.quote_plus(common.args.videoid)+'"'
        u += '&segment="'+urllib.quote_plus(str(segment))+'"'
        u += '&guid="'+urllib.quote_plus(self.GUID)+'"'
        item=xbmcgui.ListItem(self.displayname)
        item.setInfo( type="Video", infoLabels=self.infoLabels)
        item.setProperty('IsPlayable', 'true')
        common.playlist.add(url=u, listitem=item)
    
    def time2ms( self, time):
        hour,minute,seconds = time.split(';')[0].split(':')
        frame = int((float(time.split(';')[1])/24)*1000)
        milliseconds = (((int(hour)*60*60)+(int(minute)*60)+int(seconds))*1000)+frame
        return milliseconds

    def NetworkPreroll( self ):
        url = 'http://r.hulu.com/videos?eid='+common.args.eid+'&include=video_assets&include_eos=1&_language=en&_package_group_id=1&_region=US'
        data=common.getFEED(url)
        tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        networkPreroll = tree.find('show').find('link-url').string
        name = tree.find('channel').string
        infoLabels={ "Title":name }
        item = xbmcgui.ListItem(name+' Intro',path=networkPreroll)
        item.setInfo( type="Video", infoLabels=infoLabels)
        if self.queue:
            item.setProperty('IsPlayable', 'true')
            common.playlist.add(url=networkPreroll, listitem=item)
        else:
            self.queue = True
            xbmcplugin.setResolvedUrl(common.handle, True, item)

    def playSegment( self, video_id, segment=0):
        try:
            if segments > 0: smilSoup = self.getSMIL(video_id,retry=1)
            else: smilSoup = self.getSMIL(video_id)
        except: smilSoup = self.getSMIL(video_id,retry=1)
        if smilSoup:
            finalUrl = self.selectStream(smilSoup)
            self.displayname, self.infoLabels, segments  = self.getMeta(smilSoup)
            segmentUrl = finalUrl
            if segments and segments[0] <> '':
                print segments
                segmentUrl = finalUrl
                if segment > 0:
                    startseconds = self.time2ms(segments[segment-1])
                    segmentUrl += " start="+str(startseconds)
                if len(segments) > segment:
                    stopseconds = self.time2ms(segments[segment])
                    segmentUrl += " stop="+str(stopseconds)
            item = xbmcgui.ListItem(self.displayname,path=segmentUrl)
            item.setInfo( type="Video", infoLabels=self.infoLabels)
            if self.queue:
                item.setProperty('IsPlayable', 'true')
                common.playlist.add(url=segmentUrl, listitem=item)
            else:
                self.queue = True
                xbmcplugin.setResolvedUrl(common.handle, True, item)
            return segments

    def play( self, video_id):
        if (common.settings['enable_captions'] == 'true'):
            subtitles.Main().checkCaptions(video_id)
        try: smilSoup = self.getSMIL(video_id)
        except: smilSoup = self.getSMIL(video_id,retry=1)
        if smilSoup:
            finalUrl = self.selectStream(smilSoup)
            displayname, infoLabels, segments = self.getMeta(smilSoup)
            item = xbmcgui.ListItem(displayname,path=finalUrl)
            item.setInfo( type="Video", infoLabels=infoLabels)
            if self.queue:
                item.setProperty('IsPlayable', 'true')
                common.playlist.add(url=finalUrl, listitem=item)
            else:
                self.queue = True
                if self.NoResolve:
                    xbmc.Player().play(finalUrl,item)
                else:
                    xbmcplugin.setResolvedUrl(common.handle, True, item)
                if (common.settings['enable_captions'] == 'true'):
                    subtitles.Main().PlayWaitSubtitles(video_id)
            return segments

    def getMeta( self, smilSoup ): 
        ref = smilSoup.findAll('ref')[1]
        title = ref['title']
        series_title = ref['tp:series_title']
        plot = ref['abstract']
        try:season = int(ref['tp:season_number'])
        except:season = -1
        try:episode = int(ref['tp:episode_number'])
        except:episode = -1
        displayname = series_title+' - '+str(season)+'x'+str(episode)+' - '+title
        infoLabels={ "Title":title,
                     "TVShowTitle":series_title,
                     "Plot":plot,
                     "Season":season,
                     "Episode":episode}
        try:segments = ref['tp:segments'].replace('T:','').split(',')
        except:segments = False
        return displayname, infoLabels, segments
                
    def selectStream( self, smilSoup ):         
        video=smilSoup.findAll('video')
        if video is None or len(video) == 0:
            xbmcgui.Dialog().ok('No Video Streams','SMIL did not contain video links','Geo-Blocked')
            return
        streams=[]
        selectedStream = None
        cdn = None
        qtypes=['ask', 'p011', 'p010', 'p009', 'p008', 'H264 Medium', 'H264 650K', 'H264 400K', 'VP6 400K']        
        qt = int(common.settings['quality'])
        if qt < 0 or qt > 8: qt = 0
        while qt < 8:
            qtext = qtypes[qt]
            for vid in video:
                streams.append([vid['profile'],vid['cdn'],vid['server'],vid['stream'],vid['token']])
                if qtext in vid['profile']:
                    if vid['cdn'] == common.settings['defaultcdn']:
                        selectedStream = [vid['server'],vid['stream'],vid['token']]
                        print selectedStream
                        cdn = vid['cdn']
                        break

            if qt == 0 or selectedStream != None: break
            qt += 1
        
        if qt == 0 or selectedStream == None:
            if selectedStream == None:
                #ask user for quality level
                quality=xbmcgui.Dialog().select('Please select a quality level:', [stream[0]+' ('+stream[1]+')' for stream in streams])
                print quality
                if quality!=-1:
                    selectedStream = [streams[quality][2], streams[quality][3], streams[quality][4]]
                    cdn = streams[quality][1]
                    print "stream url"
                    print selectedStream
            
        if selectedStream != None:
            server = selectedStream[0]
            stream = selectedStream[1]
            token = selectedStream[2]

            protocolSplit = server.split("://")
            pathSplit = protocolSplit[1].split("/")
            hostname = pathSplit[0]
            appName = protocolSplit[1].split(hostname + "/")[1]

            if "level3" in cdn:
                appName += "?sessionid=sessionId&" + token
                stream = stream[0:len(stream)-4]
                finalUrl = server + "?sessionid=sessionId&" + token + " app=" + appName

            elif "limelight" in cdn:
                appName += '?sessionid=sessionId&' + token
                stream = stream[0:len(stream)-4]
                finalUrl = server + "?sessionid=sessionId&" + token + " app=" + appName

            elif "akamai" in cdn:
                appName += '?sessionid=sessionId&' + token
                finalUrl = server + "?sessionid=sessionId&" + token + " app=" + appName
                
            else:
                xbmcgui.Dialog().ok('Unsupported Content Delivery Network',cdn+' is unsupported at this time')
                return

            print "item url -- > " + finalUrl
            print "app name -- > " + appName
            print "playPath -- > " + stream

            #define item
            SWFPlayer = 'http://download.hulu.com/huludesktop.swf'
            finalUrl += " playpath=" + stream + " swfurl=" + SWFPlayer + " pageurl=" + SWFPlayer
            if (common.settings['swfverify'] == 'true'):
                finalUrl += " swfvfy=true"
            return finalUrl

                           
################# OLD FUNCTIONS
# might be useful         
                
                
    def decrypt_cid(self, p):
        cidkey = '48555bbbe9f41981df49895f44c83993a09334d02d17e7a76b237d04c084e342'
        v3 = binascii.unhexlify(p)
        ecb = common.AES(binascii.unhexlify(cidkey))
        return ecb.decrypt(v3).split("~")[0]

    def cid2eid(self, p):
        import md5
        dec_cid = int(p.lstrip('m'), 36)
        xor_cid = dec_cid ^ 3735928559 # 0xDEADBEEF
        m = md5.new()
        m.update(str(xor_cid) + "MAZxpK3WwazfARjIpSXKQ9cmg9nPe5wIOOfKuBIfz7bNdat6gQKHj69ZWNWNVB1")
        value = m.digest()
        return base64.encodestring(value).replace("+", "-").replace("/", "_").replace("=", "").replace('/n','')

    def decrypt_pid(self, p):
        import re
        cp_strings = [
            '6fe8131ca9b01ba011e9b0f5bc08c1c9ebaf65f039e1592d53a30def7fced26c',
            'd3802c10649503a60619b709d1278ffff84c1856dfd4097541d55c6740442d8b',
            'c402fb2f70c89a0df112c5e38583f9202a96c6de3fa1aa3da6849bb317a983b3',
            'e1a28374f5562768c061f22394a556a75860f132432415d67768e0c112c31495',
            'd3802c10649503a60619b709d1278efef84c1856dfd4097541d55c6740442d8b'
        ]

        v3 = p.split("~")
        v3a = binascii.unhexlify(v3[0])
        v3b = binascii.unhexlify(v3[1])

        ecb = common.AES(v3b)
        tmp = ecb.decrypt(v3a)

        for v1 in cp_strings[:]:
            ecb = common.AES(binascii.unhexlify(v1))
            v2 = ecb.decrypt(tmp)
            if (re.match("[0-9A-Za-z_-]{32}", v2)):
                return v2

    def pid_auth(self, pid):
        import md5
        m=md5.new()
        m.update(str(pid) + "yumUsWUfrAPraRaNe2ru2exAXEfaP6Nugubepreb68REt7daS79fase9haqar9sa")
        return m.hexdigest()
