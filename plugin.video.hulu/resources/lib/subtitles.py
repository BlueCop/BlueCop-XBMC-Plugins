import xbmc
import xbmcgui
import xbmcplugin
import common
import os
import binascii
import re
import math

import datetime


from BeautifulSoup import BeautifulSoup

try:
    from xml.etree import ElementTree
except:
    from elementtree import ElementTree

subdeckeys  = [ common.xmldeckeys[0] ]

class Main:
    def __init__( self ):
        pass

    def PlayWaitSubtitles(self, video_id):
        while not xbmc.Player().isPlaying():
            print 'HULU --> Not Playing'
            xbmc.sleep(100)
        self.SetSubtitles(video_id)
    
    def SetSubtitles(self, video_id):
        subtitles = os.path.join(common.pluginpath,'resources','cache',video_id+'.srt')
        self.checkCaptions(video_id)
        if os.path.isfile(subtitles) and xbmc.Player().isPlaying():
            print "HULU --> Subtitles Enabled."
            xbmc.Player().setSubtitles(subtitles)
        elif xbmc.Player().isPlaying():
            print "HULU --> Subtitles Disabled."
        else:
            print "HULU --> No Media Playing. Subtitles Not Assigned."
        
    def checkCaptions(self, video_id):
        subtitles = os.path.join(common.pluginpath,'resources','cache',video_id+'.srt')
        if os.path.isfile(subtitles):
            print "HULU --> Using Cached Subtitles"
        else:
            url = 'http://www.hulu.com/captions?content_id='+video_id
            xml = common.getFEED(url)
            tree = ElementTree.XML(xml)
            hasSubs = tree.findtext('en')
            if(hasSubs):
                print "HULU --> Grabbing subtitles..."
                subtitles = self.convert_subtitles(hasSubs)
                common.SaveFile(os.path.join(common.pluginpath,'resources','cache',video_id+'.srt'), subtitles)
                print "HULU: --> Successfully converted subtitles to SRT"
            else:
                print "HULU --> No subtitles available."
                
    def convert_subtitles(self, url):
        xml=common.getFEED(url)
        tree = ElementTree.XML(xml)
        lines = tree.find('BODY').findall('SYNC')
        srt_output = ''
        count = 1
        displaycount = 1
        for line in lines:
            if(line.get('Encrypted') == 'true'):
                sub = self.decrypt_subs(line.text)
            else:
                sub = line.text
            sub = self.clean_subs(sub)
            if sub == '':
                count += 1
                continue
            start = self.convert_time(int(line.get('start')))
            if count < len(lines):
                end = self.convert_time(int(lines[count].get('start')))
            line = str(displaycount)+"\n"+start+" --> "+end+"\n"+sub+"\n\n"
            srt_output += line
            count += 1
            displaycount += 1
        return srt_output

    def decrypt_subs(self, encsubs):
        encdata = binascii.unhexlify(encsubs)
        for key in subdeckeys[:]:
            cbc = common.AES_CBC(binascii.unhexlify(key[0]))
            subs = cbc.decrypt(encdata,key[1])
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
        sub = sub.replace('&#160;',' ').strip()
        if sub <> '':
            sub = BeautifulSoup(sub,convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0].string.encode( "utf-8" )
            sub = BeautifulSoup(sub,convertEntities=BeautifulSoup.XML_ENTITIES).contents[0].string.encode( "utf-8" )
        return sub

    def convert_time(self, milliseconds):
        seconds = int(float(milliseconds)/1000)
        milliseconds -= (seconds*1000)
        hours = seconds / 3600
        seconds -= 3600*hours
        minutes = seconds / 60
        seconds -= 60*minutes
        return "%02d:%02d:%02d,%3d" % (hours, minutes, seconds, milliseconds)
