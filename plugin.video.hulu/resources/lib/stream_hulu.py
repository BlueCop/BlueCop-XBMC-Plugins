import xbmc
import xbmcgui
import xbmcplugin
import common
import re
import sys
import binascii
import md5
import base64
import math
import os
import hmac
import operator
import random
import time
import urllib
from array import array
#from aes import AES
from crypto.cipher.cbc      import CBC
from crypto.cipher.base     import noPadding
from crypto.cipher.rijndael import Rijndael
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

pluginhandle = int(sys.argv[1])

xmldeckeys = [
             ['4878B22E76379B55C962B18DDBC188D82299F8F52E3E698D0FAF29A40ED64B21', 'WA7hap7AGUkevuth'],
             ['246DB3463FC56FDBAD60148057CB9055A647C13C02C64A5ED4A68F81AE991BF5', 'vyf8PvpfXZPjc7B1'],
             ['8CE8829F908C2DFAB8B3407A551CB58EBC19B07F535651A37EBC30DEC33F76A2', 'O3r9EAcyEeWlm5yV'],
             ['852AEA267B737642F4AE37F5ADDF7BD93921B65FE0209E47217987468602F337', 'qZRiIfTjIGi3MuJA'],
             ['76A9FDA209D4C9DCDFDDD909623D1937F665D0270F4D3F5CA81AD2731996792F', 'd9af949851afde8c'],
             ['1F0FF021B7A04B96B4AB84CCFD7480DFA7A972C120554A25970F49B6BADD2F4F', 'tqo8cxuvpqc7irjw'],
             ['3484509D6B0B4816A6CFACB117A7F3C842268DF89FCC414F821B291B84B0CA71', 'SUxSFjNUavzKIWSh'],
             ['B7F67F4B985240FAB70FF1911FCBB48170F2C86645C0491F9B45DACFC188113F', 'uBFEvpZ00HobdcEo'],
             ['40A757F83B2348A7B5F7F41790FDFFA02F72FC8FFD844BA6B28FD5DFD8CFC82F', 'NnemTiVU0UA5jVl0'],
             ['d6dac049cc944519806ab9a1b5e29ccfe3e74dabb4fa42598a45c35d20abdd28', '27b9bedf75ccA2eC']
             ]

subdeckeys = [
             ['4878B22E76379B55C962B18DDBC188D82299F8F52E3E698D0FAF29A40ED64B21', 'WA7hap7AGUkevuth']
             ]

smildeckeys = [
              ['d6dac049cc944519806ab9a1b5e29ccfe3e74dabb4fa42598a45c35d20abdd28', '27b9bedf75ccA2eC']
              ]

class ResumePlayer( xbmc.Player ) :            
    def __init__ ( self ):
        xbmc.Player.__init__( self )
        self.player_playing = False
        self.content_id=common.args.url
        
    def onPlayBackStarted(self):
        print 'HULU --> onPlayBackStarted'
        if common.settings['enable_login']=='true' and common.settings['usertoken']:
            if self.player_playing:
                self.seekPlayback()
                if common.settings['enable_login']=='true' and common.settings['usertoken']:
                    action = "event"
                    app = "f8aa99ec5c28937cf3177087d149a96b5a5efeeb"
                    parameters = {'event_type':'view',
                                  'token':common.settings['usertoken'],
                                  'target_type':'video',
                                  'id':common.args.videoid,
                                  'app':app}
                    common.postAPI(action,parameters,False)
                    print "HULU --> Posted view"
                    #self.p.onPlayBackStarted()
            self.player_playing = True
            while self.player_playing:
                try:
                    xbmc.sleep(1000)
                    self.stoptime = self.getTime()
                except:
                    pass

    def onPlayBackStopped(self):
        if common.settings['enable_login']=='true' and common.settings['usertoken']:
            print "HULU --> onPlayBackStopped "+str(self.stoptime)
            common.postSTOP( 'stop',self.content_id, self.stoptime )
            self.player_playing = False

    def onPlayBackEnded(self):
        if common.settings['enable_login']=='true' and common.settings['usertoken']:
            print "HULU --> onPlayBackEnded"
            common.postSTOP( 'stop',self.content_id, self.stoptime )
            action = "event"
            app = "f8aa99ec5c28937cf3177087d149a96b5a5efeeb"
            parameters = {'event_type':'view_complete',
                          'token':common.settings['usertoken'],
                          'target_type':'video',
                          'id':common.args.videoid,
                          'app':app}
            common.postAPI(action,parameters,False)
            print "HULU --> Posted view_complete complete"
            self.player_playing = False

    def seekPlayback(self):
        if common.settings['enable_login']=='true' and common.settings['usertoken']:
            try:
                url = 'http://www.hulu.com/pt/position?content_id='+self.content_id+'&format=xml&token='+common.settings['usertoken']
                data= common.getFEED(url)
                tree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
                position = float(tree.find('position').string)
                should_resume = tree.find('should_resume').string
                if should_resume == '1':
                    self.seekTime(position)
            except: print 'HULU --> failed to seek'

class Main:

    def __init__( self ):
        self.GUID = self.makeGUID()
        video_id=common.args.url
        queue=False
        self.playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #PREROLL
        preroll = common.settings['prerollads']
        if preroll > 0:
            for i in range(0,preroll):
                try:
                    self.playAD(video_id,str(i),queue=queue)
                    queue=True
                except: break 
                #xbmc.sleep(1000)    

        self.play(video_id,queue=queue)

        #POSTROLL
        postroll = common.settings['totalads']
        if postroll > 0:
            for i in range(preroll,postroll):
                try: self.playAD(video_id,str(i),queue=queue)
                except: break
                #xbmc.sleep(1000)

    def AES(self,key):
        return Rijndael(key, keySize=32, blockSize=16, padding=noPadding())

    def AES_CBC(self,key):
        return CBC(blockCipherInstance=self.AES(key))
        
    def decrypt_cid(self, p):
        cidkey = '48555bbbe9f41981df49895f44c83993a09334d02d17e7a76b237d04c084e342'
        v3 = binascii.unhexlify(p)
        ecb = self.AES(binascii.unhexlify(cidkey))
        return ecb.decrypt(v3).split("~")[0]

    def cid2eid(self, p):
        dec_cid = int(p.lstrip('m'), 36)
        xor_cid = dec_cid ^ 3735928559 # 0xDEADBEEF
        m = md5.new()
        m.update(str(xor_cid) + "MAZxpK3WwazfARjIpSXKQ9cmg9nPe5wIOOfKuBIfz7bNdat6gQKHj69ZWNWNVB1")
        value = m.digest()
        return base64.encodestring(value).replace("+", "-").replace("/", "_").replace("=", "")

    def makeGUID(self):
        guid = ''
        for i in range(8):
            number = "%0.2X" % (int( ( 1.0 + random.random() ) * 0x10000) | 0)
            guid += number[2:]
        return guid

    def decrypt_pid(self, p):
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

        ecb = self.AES(v3b)
        tmp = ecb.decrypt(v3a)

        for v1 in cp_strings[:]:
            ecb = self.AES(binascii.unhexlify(v1))
            v2 = ecb.decrypt(tmp)
            if (re.match("[0-9A-Za-z_-]{32}", v2)):
                return v2

    def pid_auth(self, pid):
        m=md5.new()
        m.update(str(pid) + "yumUsWUfrAPraRaNe2ru2exAXEfaP6Nugubepreb68REt7daS79fase9haqar9sa")
        return m.hexdigest()

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
        for key in smildeckeys[:]:
            cbc = self.AES_CBC(binascii.unhexlify(key[0]))
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

    def decrypt_subs(self, encsubs):
        encdata = binascii.unhexlify(encsubs)
        for key in subdeckeys[:]:
            cbc = self.AES_CBC(binascii.unhexlify(key[0]))
            subs = cbc.decrypt(encdata,key[1])
            
            substart = subs.find("<P")
            if (substart > -1):
                #print key
                i = subs.rfind("</P>")
                subs = subs[substart:i+4]
                return subs

    def clean_subs(self, data):
        br = re.compile(r'<br.*?>')
        tag = re.compile(r'<.*?>')
        space = re.compile(r'\s\s\s+')
        sub = br.sub('\n', data)
        sub = tag.sub(' ', sub)
        sub = space.sub(' ', sub)
        return sub

    def convert_time(self, seconds):
        hours = seconds / 3600
        seconds -= 3600*hours
        minutes = seconds / 60
        seconds -= 60*minutes
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

    def convert_subtitles(self, subtitles, output):
        subtitle_data = subtitles
        subtitle_data = subtitle_data.replace("\n","").replace("\r","")
        subtitle_data = BeautifulStoneSoup(subtitle_data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        subtitle_array = []
        srt_output = ''

        print "HULU: --> Converting subtitles to SRT"
        #self.update_dialog('Converting Subtitles to SRT')
        lines = subtitle_data.findAll('sync') #split the file into lines
        for line in lines:
            if(line['encrypted'] == 'true'):
                sub = self.decrypt_subs(line.string)
                sub = self.clean_subs(sub)
                sub = unicode(BeautifulStoneSoup(sub,convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )

            else:
                sub = unicode(BeautifulStoneSoup(sub,convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]).encode( "utf-8" )

            begin_time = int(line['start'])
            seconds = int(math.floor(begin_time/1000))
            milliseconds = int(begin_time - (seconds * 1000))
            timestamp = self.convert_time(seconds)
            timestamp = "%s,%03d" % (timestamp, milliseconds)

            index = len(subtitle_array)-1
            if(index > -1 and subtitle_array[index]['end'] == None):
                millsplit = subtitle_array[index]['start'].split(',')
                itime = millsplit[0].split(':')
                start_seconds = (int(itime[0])*60*60)+(int(itime[1])*60)+int(itime[2])
                end_seconds = start_seconds + 4
                if end_seconds < seconds:
                    endmilliseconds = int(millsplit[1])
                    endtimestamp = self.convert_time(end_seconds)
                    endtimestamp = "%s,%03d" % (endtimestamp, endmilliseconds)
                    subtitle_array[index]['end'] = endtimestamp
                else:
                    subtitle_array[index]['end'] = timestamp

            if sub != '&#160; ':
                sub = sub.replace('&#160;', ' ')
                temp_dict = {'start':timestamp, 'end':None, 'text':sub}
                subtitle_array.append(temp_dict)

        for i, subtitle in enumerate(subtitle_array):
            line = str(i+1)+"\n"+str(subtitle['start'])+" --> "+str(subtitle['end'])+"\n"+str(subtitle['text'])+"\n\n"
            srt_output += line
        
        file = open(os.path.join(common.pluginpath,'resources','cache',output+'.srt'), 'w')
        file.write(srt_output)
        file.close()
        print "HULU: --> Successfully converted subtitles to SRT"
        #self.update_dialog('Conversion Complete')
        return True

    def checkCaptions(self, video_id):
        url = 'http://www.hulu.com/captions?content_id='+video_id
        html = common.getHTML(url)
        capSoup = BeautifulStoneSoup(html)
        hasSubs = capSoup.find('en')
        if(hasSubs):
            print "HULU --> Grabbing subtitles..."
            #self.update_dialog('Downloading Subtitles')
            html=common.getHTML(hasSubs.string)
            ok = self.convert_subtitles(html,video_id)
            if ok:
                print "HULU --> Subtitles enabled."
                #self.update_dialog('Subtitles Completed Successfully')
            else:
                print "HULU --> There was an error grabbing the subtitles."
                #self.update_dialog('Error Downloading Subtitles')

        else:
            print "HULU --> No subtitles available."
            #self.update_dialog('No Subtitles Available')

    def getSMIL(self, video_id):
        try:
            epoch = int(time.mktime(time.gmtime()))
            parameters = {'video_id': video_id,
                          'v'       : '888324234',
                          'ts'      : str(epoch),
                          'np'      : '1',
                          'vp'      : '1',
                          'device_id' : self.GUID,
                          'pp'      : 'Desktop',
                          'dp_id'   : 'Hulu',
                          'region'  : 'US',
                          'ep'      : '1',
                          'language': 'en'
                          }
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
            smilXML=common.getFEED(smilURL)
            smilXML=self.decrypt_SMIL(smilXML)
            if smilXML:
                smilSoup=BeautifulStoneSoup(smilXML, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
                print smilSoup.prettify()
                return smilSoup
            else:
                return False
        except:
            heading = 'SMIL ERROR'
            message = 'Error retrieving SMIL file'
            duration = 8000
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
            #xbmcgui.Dialog().ok('Synchronized Multimedia Integration Language File Error','Error retrieving or decrypting the SMIL file.')
            return False
    
    def ADencrypt(self, data, iv):
        key = '9dbb5e376e65a64324e9269775dafd5b83c38f1d8819d5f1dc4ec2083c081bdb'
        cbc = self.AES_CBC(binascii.unhexlify(key))
        encdata = cbc.encrypt(data,base64.decodestring(iv))
        return base64.encodestring(encdata).replace('\n','')

    def ADdecrypt(self, data, iv):
        key = '9d489e6c3adfb6a00a23eb7afc8944affd180546c719db5393e2d4177e40c77d'
        bindata = base64.decodestring(data)
        bindata = bindata[1:]
        cbc = self.AES_CBC(binascii.unhexlify(key))
        return cbc.decrypt(bindata,base64.decodestring(iv))[16:]
  
    def MakeIV(self):
        data = self.makeGUID()+self.makeGUID()[:8]
        data = binascii.unhexlify(data)
        return base64.encodestring(data)
        
    def playAD(self, video_id,pod,queue=False):
        try:
            session=self.sstate
            state=self.ustate
        except:
            session=''
            state=''
        epoch = str(int(time.mktime(time.gmtime())))
        xmlbase='''
<AdRequest Pod="'''+pod+'''" SessionState="'''+session+'''" ResponseType="VAST" Timestamp="'''+epoch+'''">
  <Distributor Name="Hulu" Platform="Desktop"/>
  <Visitor IPV4Address="" BT_RSSegments="null" UserId="-1" MiniCount="" MiniDuration="" ComputerGuid="'''+self.GUID+'''" AdFeedback="null" PlanId="0" FlashVersion="WIN 11,1,102,55" State="'''+state+'''"/>
  <KeyValues>
    <KeyValue Key="env" Value="prod"/>
    <KeyValue Key="version" Value="Voltron"/>
  </KeyValues>
  <SiteLocation>
    <VideoPlayer Url="http://download.hulu.com/huludesktop.swf" Mode="normal">
      <VideoAsset PId="NO_MORE_RELEASES_PLEASE_'''+video_id+'''" Id="'''+video_id+'''" ContentLanguage="en" BitRate="650" Width="320" Height="240"/>
    </VideoPlayer>
  </SiteLocation>
  <Diagnostics/>
</AdRequest>'''
        #print xmlbase
        IV = self.MakeIV()
        encdata = self.ADencrypt(xmlbase,IV)
        url = 'http://p.hulu.com/getPlaylist?kv=1&iv='+urllib.quote_plus(IV)
        encplaylist = common.getFEED(url,postdata=encdata)
        playlist = self.ADdecrypt(encplaylist, IV)
        playlistSoup=BeautifulStoneSoup(playlist, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        print playlistSoup.prettify()
        self.sstate = playlistSoup.find('sessionstate')['value']                                       
        self.ustate = playlistSoup.find('userstate')['value']
        mediafiles = playlistSoup.findAll('mediafile')
        if common.settings['adquality'] <= len(mediafiles):
            mediaUrl = mediafiles[common.settings['adquality']].string
        else:
            mediaUrl = mediafiles[0].string
        adtitle = playlistSoup.find('adtitle').string
        item = xbmcgui.ListItem(adtitle, path=mediaUrl)
        item.setInfo( type="Video", infoLabels={ "Title":adtitle})
        if queue:
            item.setProperty('IsPlayable', 'true')
            self.playlist.add(url=mediafiles[0].string, listitem=item)
        else:
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)
        for item in playlistSoup.findAll('tracking'):
            common.getFEED(item.string)
    
    def play( self, video_id, queue ):
        print 'Video ID: '+video_id
        if (common.settings['enable_captions'] == 'true'):
            self.checkCaptions(video_id)
        #getSMIL
        smilSoup = self.getSMIL(video_id)
        if smilSoup:
            ref = smilSoup.findAll('ref')[1]
            title = ref['title']
            series_title = ref['tp:series_title']
            try:season = int(ref['tp:season_number'])
            except:season = -1
            try:episode = int(ref['tp:episode_number'])
            except:episode = -1
            
            #getRTMP
            video=smilSoup.findAll('video')
            streams=[]
            selectedStream = None
            cdn = None
            qtypes=['ask', 'p011', 'p010', 'p009', 'p008', 'H264 Medium', 'H264 650K', 'H264 400K', 'VP6 400K']        
            #label streams
            qt = int(common.settings['quality'])
            if qt < 0 or qt > 8: qt = 0
            while qt < 8:
                qtext = qtypes[qt]
                for vid in video:
                    #if qt == 0:
                    streams.append([vid['profile'],vid['cdn'],vid['server'],vid['stream'],vid['token']])
                    #if qt > 6 and 'H264' in vid['profile']: continue
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
                #form proper streaming url
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
                    newUrl = server + "?sessionid=sessionId&" + token + " app=" + appName
    
                elif "limelight" in cdn:
                    appName += '?sessionid=sessionId&' + token
                    stream = stream[0:len(stream)-4]
                    newUrl = server + "?sessionid=sessionId&" + token + " app=" + appName
    
                elif "akamai" in cdn:
                    appName += '?sessionid=sessionId&' + token
                    newUrl = server + "?sessionid=sessionId&" + token + " app=" + appName
                    
                else:
                    xbmcgui.Dialog().ok('Unsupported Content Delivery Network',cdn+' is unsupported at this time')
                    return
    
                print "item url -- > " + newUrl
                print "app name -- > " + appName
                print "playPath -- > " + stream
    
                #define item
                SWFPlayer = 'http://download.hulu.com/huludesktop.swf'
                newUrl += " playpath=" + stream + " swfurl=" + SWFPlayer + " pageurl=" + SWFPlayer
                if (common.settings['swfverify'] == 'true'):
                    newUrl += " swfvfy=true"
                
                item = xbmcgui.ListItem(title,path=newUrl)
                item.setInfo( type="Video", infoLabels={ "Title":title,
                                                         "TVShowTitle":series_title,
                                                         "Season":season,
                                                         "Episode":episode})
                if queue:
                    item.setProperty('IsPlayable', 'true')
                    self.playlist.add(url=newUrl, listitem=item)
                else:
                    self.p=ResumePlayer()
                    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                    while not self.p.isPlaying():
                        print 'HULU --> Not Playing'
                        xbmc.sleep(100)
                    #Enable Subtitles
                    subtitles = os.path.join(common.pluginpath,'resources','cache',video_id+'.srt')
                    if (common.settings['enable_captions'] == 'true') and os.path.isfile(subtitles):
                        print "HULU --> Setting subtitles"
                        self.p.setSubtitles(subtitles)
