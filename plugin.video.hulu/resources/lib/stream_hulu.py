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
from array import array
from aes import AES
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
             ['40A757F83B2348A7B5F7F41790FDFFA02F72FC8FFD844BA6B28FD5DFD8CFC82F', 'NnemTiVU0UA5jVl0']
             ]

subdeckeys = [
             ['4878B22E76379B55C962B18DDBC188D82299F8F52E3E698D0FAF29A40ED64B21', 'WA7hap7AGUkevuth']
             ]

smildeckeys = [
             ['40A757F83B2348A7B5F7F41790FDFFA02F72FC8FFD844BA6B28FD5DFD8CFC82F', 'NnemTiVU0UA5jVl0']
             ]


class Main:

    def __init__( self ):
        #Initialize playback progress dialog
        #self.pDialog = xbmcgui.DialogProgress()
        #self.Heading = 'Hulu'
        #self.text1 = 'Preparing for Playback'
        #self.text2 = ''
        #self.text3 = ''
        #self.pDialog.create(self.Heading)
        #self.pDialog.update(0 , self.text1, self.text2, self.text3)
        #select from avaliable streams, then play the file
        self.play()
        
    def decrypt_cid(self, p):
        cidkey = '48555bbbe9f41981df49895f44c83993a09334d02d17e7a76b237d04c084e342'
        v3 = binascii.unhexlify(p)
        ecb = AES(binascii.unhexlify(cidkey))
        return ecb.decrypt(v3).split("~")[0]

    def cid2eid(self, p):
        dec_cid = int(p.lstrip('m'), 36)
        xor_cid = dec_cid ^ 3735928559
        m = md5.new()
        m.update(str(xor_cid) + "MAZxpK3WwazfARjIpSXKQ9cmg9nPe5wIOOfKuBIfz7bNdat6gQKHj69ZWNWNVB1")
        value = m.digest()
        return base64.encodestring(value).replace("+", "-").replace("/", "_").replace("=", "")

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

        ecb = AES(v3b)
        tmp = ecb.decrypt(v3a)

        for v1 in cp_strings[:]:
            ecb = AES(binascii.unhexlify(v1))
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

        for key in smildeckeys[:]:
            smil=""
            out=[0,0,0,0]
            ecb = AES(binascii.unhexlify(key[0]))
            unaes = ecb.decrypt(encdata)

            xorkey = array('i',key[1])

            for i in range(0, len(encdata)/16):
                x = unaes[i*16:i*16+16]
                res = array('i',x)
                for j in range(0,4):
                    out[j] = res[j] ^ xorkey[j]
                x = encdata[i*16:i*16+16]
                xorkey = array('i',x)
                a=array('i',out)
                x=a.tostring()
                smil = smil + x

            if (smil.find("<smil") == 0):
                print key
                i = smil.rfind("</smil>")
                smil = smil[0:i+7]
                return smil

    def decrypt_subs(self, encsubs):
        encdata = binascii.unhexlify(encsubs)

        for key in subdeckeys[:]:
            subs=""
            out=[0,0,0,0]
            ecb = AES(binascii.unhexlify(key[0]))
            unaes = ecb.decrypt(encdata)
            xorkey = array('i',key[1])

            for i in range(0, len(encdata)/16):
                x = unaes[i*16:i*16+16]
                res = array('i',x)
                for j in range(0,4):
                    out[j] = res[j] ^ xorkey[j]
                x = encdata[i*16:i*16+16]
                xorkey = array('i',x)
                a=array('i',out)
                x=a.tostring()
                subs += x

            substart = subs.find("<P")

            if (substart > -1):
                print key
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
        
        file = open(os.path.join(os.getcwd().replace(';', ''),'resources','cache',output+'.srt'), 'w')
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
            import time
            epoch = int(time.mktime(time.gmtime()))
            parameters = {'video_id': video_id,
                          'v'       : '850037518',
                          'ts'      : str(epoch),
                          'np'      : '1',
                          'vp'      : '1',
                          'pp'      : 'Desktop',
                          'dp_id'   : 'Hulu',
                          'region'  : 'US',
                          'language': 'en'
                          }
            smilURL =  'http://s.hulu.com/select'
            smilURL += '?video_id='+parameters['video_id']
            smilURL += '&v='+parameters['v']
            smilURL += '&ts='+parameters['ts']
            smilURL += '&np='+parameters['np']
            smilURL += '&vp='+parameters['vp']
            smilURL += '&pp='+parameters['pp']
            smilURL += '&dp_id='+parameters['dp_id']
            if common.settings['enable_login']=='true' and common.settings['enable_plus']=='true' and common.settings['usertoken']:
                parameters['ep'] = '1'
                parameters['token'] = common.settings['usertoken']
                smilURL += '&token='+parameters['token']
                smilURL += '&ep='+parameters['ep']
            smilURL += '&region='+parameters['region']
            smilURL += '&language='+parameters['language']
            smilURL += '&bcs='+self.content_sig(parameters)
            print 'HULU --> SMILURL: ' + smilURL
            #self.update_dialog('Grabbing SMIL File')
            smilXML=common.getFEED(smilURL)
            #self.update_dialog('Decrypting SMIL File')
            tmp=self.decrypt_SMIL(smilXML)
            smilSoup=BeautifulStoneSoup(tmp, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            return smilSoup
        except:
            heading = 'SMIL ERROR'
            message = 'Error retrieving SMIL file'
            duration = 8000
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )
            #xbmcgui.Dialog().ok('Synchronized Multimedia Integration Language File Error','Error retrieving or decrypting the SMIL file.')
            return False

    def update_dialog( self, newline ):
        if self.text2 == '':
            self.text2 = newline
            self.pDialog.update(0 , self.text1, self.text2, self.text3)
        elif self.text3 == '':
            self.text3 = newline
            self.pDialog.update(0 , self.text1, self.text2, self.text3)
        else:
            self.text1 = self.text2
            self.text2 = self.text3
            self.text3 = newline
            self.pDialog.update(0 , self.text1, self.text2, self.text3)
    
    def play( self ):
        video_id=common.args.url
        print 'Video ID: '+video_id
        #self.update_dialog('Playing Video ID: '+video_id)

        #get closed captions/subtitles
        if (common.settings['enable_captions'] == 'true'):
            #self.update_dialog('Subtitles Enabled')
            self.checkCaptions(video_id)
        #else:
            #self.update_dialog('Subtitles Disabled')

        #getSMIL
        smilSoup = self.getSMIL(video_id)
        print smilSoup.prettify()

        #self.update_dialog('Selecting Video Stream')
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
        qtypes=['ask', 'p011', 'p010', 'p008', 'H264 Medium', 'H264 650K', 'H264 400K', 'High', 'Medium','Low']        
        #label streams
        qt = int(common.settings['quality'])
        if qt < 0 or qt > 9: qt = 0
        while qt < 9:
            qtext = qtypes[qt]
            for vid in video:
                #if qt == 0:
                streams.append([vid['profile'],vid['cdn'],vid['server'],vid['stream'],vid['token']])
                if qt > 6 and 'H264' in vid['profile']: continue
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
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

            #Enable Subtitles
            subtitles = os.path.join(os.getcwd().replace(';', ''),'resources','cache',video_id+'.srt')
            if (common.settings['enable_captions'] == 'true') and os.path.isfile(subtitles):
                print "HULU --> Setting subtitles"
                import time
                time.sleep(4)
                xbmc.Player().setSubtitles(subtitles)
            #if common.settings['enable_login']=='true' and common.settings['usertoken']:     
            #    action = "event"
            #    app = "f8aa99ec5c28937cf3177087d149a96b5a5efeeb"
            #    parameters = {'event_type':'view',
            #                  'token':common.settings['usertoken'],
            #                  'target_type':'video',
            #                  'id':video_id,
            #                  'app':app}
            #    common.postAPI(action,parameters,False)
            #    print "Posted view to Hulu"

