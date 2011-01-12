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

class Main:

    def __init__( self ):
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

    def content_sig(self, pid):
        hmac_key = 'f6daaa397d51f568dd068709b0ce8e93293e078f7dfc3b40dd8c32d36d2b3ce1'
        parameters = {'video_id' : pid,
                      'v' : '850037518',
                      'ts' : '1294866343',
                      'np' : '1',
                      'vp' : '1',
                      'pp' : 'hulu',
                      'dp_id' : 'hulu'}
        sorted_parameters = sorted(parameters.iteritems(), key=operator.itemgetter(0))
        data = ''
        for item1, item2 in sorted_parameters:
            data += item1 + item2
        sig = hmac.new(hmac_key, data)
        return sig.hexdigest()

    def pid_auth(self, pid):
        m=md5.new()
        m.update(str(pid) + "yumUsWUfrAPraRaNe2ru2exAXEfaP6Nugubepreb68REt7daS79fase9haqar9sa")
        return m.hexdigest()

    def decrypt_SMIL(self, encsmil):
        encdata = binascii.unhexlify(encsmil)

        for key in xmldeckeys[:]:
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
                i = smil.rfind("</smil>")
                smil = smil[0:i+7]
                return smil

    def decrypt_subs(self, encsubs):
        encdata = binascii.unhexlify(encsubs)

        for key in xmldeckeys[:]:
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

        file = open('special://temp/'+output+'.srt', 'w')
        file.write(srt_output)
        file.close()
        print "HULU: --> Successfully converted subtitles to SRT"
        return True

    def checkCaptions(self, pid):
        html = common.getHTML('http://www.hulu.com/videos/transcripts/'+pid+'.xml')
        capSoup = BeautifulStoneSoup(html)
        hasSubs = capSoup.find('en')
        if(hasSubs):
            print "HULU --> Grabbing subtitles..."
            html=common.getHTML(hasSubs.string)
            ok = self.convert_subtitles(html,pid)
            if ok:
                print "HULU --> Subtitles enabled."
            else:
                print "HULU --> There was an error grabbing the subtitles."
        else:
            print "HULU --> No subtitles available."

    def play( self ):
        print common.args.url
        if 'http://' in common.args.url:
            #getCID
            html=common.getHTML(common.args.url)
            p=re.compile('so.addVariable\("content_id", "(.+?)"\);')
            ecid=p.findall(html)[0]
            cid=self.decrypt_cid(ecid)

            #getEID
            eid=self.cid2eid(cid)
            #grab eid from failsafe url
            #p=re.compile('<embed src="http://www.hulu.com/embed/(.+?)" type="application/x-shockwave-flash" allowFullScreen="true"')
            #eid=p.findall(html)[0]
            eidurl="http://r.hulu.com/videos?eid="+eid

            #getPID
            html=common.getHTML(eidurl)
            cidSoup=BeautifulStoneSoup(html)
            pid=cidSoup.findAll('pid')[0].contents[0]
            pid=self.decrypt_pid(pid)
        else:
            pid=common.args.url

        #get closed captions/subtitles
        print common.settings['enable_captions']
        #if (common.settings['enable_captions'] == 'true'):
        #    self.checkCaptions(pid)

        #getSMIL
        try:
            #smilURL = "http://s.hulu.com/select.ashx?pid=" + pid + "&auth=" + self.pid_auth(pid) + "&v=713434170&np=1&pp=hulu&dp_id=hulu&cb=499"
            smilURL = 'http://s.hulu.com/select?video_id=' + pid + '&v=850037518&ts=1294866343&np=1&vp=1&pp=hulu&dp_id=hulu&&bcs=' + self.content_sig(pid)
            print 'HULU --> SMILURL: ' + smilURL
            smilXML=common.getHTML(smilURL)
            tmp=self.decrypt_SMIL(smilXML)
            smilSoup=BeautifulStoneSoup(tmp, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            print smilSoup.prettify()
        except:
            xbmcgui.Dialog().ok('Synchronized Multimedia Integration Language File Error','Error retrieving or decrypting the SMIL file.')
            return
        
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
                if qt == 0:
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
                appName += "?" + token
                stream = stream[0:len(stream)-4]
                newUrl = server + " app=" + appName

            elif "limelight" in cdn:
                appName += '?' + token
                stream = stream[0:len(stream)-4]
                newUrl = server + '?' + token + " app=" + appName

            elif "akamai" in cdn:
                appName += '?' + token
                newUrl = server + '?' + token
                #newUrl = server + "?_fcs_vhost=" + hostname + "&" + token

            else:
                xbmcgui.Dialog().ok('Unsupported Content Delivery Network',cdn+' is unsupported at this time')
                return

            print "item url -- > " + newUrl
            print "app name -- > " + appName
            print "playPath -- > " + stream

            #define item
            SWFPlayer = 'http://www.hulu.com/site-player/72770/playback.swf'
            newUrl += " playpath=" + stream + " swfurl=" + SWFPlayer
            if (common.settings['swfverify'] == 'true'):
                newUrl += " swfvfy=true"
            
            item = xbmcgui.ListItem(path=newUrl)
            xbmcplugin.setResolvedUrl(pluginhandle, True, item)

            #Enable Subtitles
            subtitles = 'special://temp/'+pid+'.srt'
            if (common.settings['enable_captions'] == 'true') and os.path.isfile(subtitles):
                print "HULU --> Setting subtitles"
                import time
                time.sleep(4)
                xbmc.Player().setSubtitles(subtitles)

