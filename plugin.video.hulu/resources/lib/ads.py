import xbmc
import xbmcgui
import xbmcplugin
import common
import sys
import os
import time
import binascii
import base64
import urllib

from BeautifulSoup import BeautifulStoneSoup

class Main:
    def __init__( self ):
        pass

    def PreRoll(self,video_id,GUID,queue):
        addcount = 0
        preroll = common.settings['prerollads']
        if preroll > 0:
            if queue:
                self.queueAD(video_id,preroll,addcount,GUID)
            else:
                self.playAD(video_id,addcount,GUID)
                addcount += 1
                if preroll > 1:
                    self.queueAD(video_id,preroll,addcount,GUID)
                    addcount += preroll - 1
        return addcount
    
    def Trailing(self,addcount,video_id,GUID):
        postroll = common.settings['trailads']
        if postroll > 0:
            self.queueAD(video_id,addcount+postroll,addcount,GUID)
        return
        
    def queueAD(self, video_id,stop,start=0,GUID=''):
        for pod in range(start,stop):
            mode='AD_play'
            u = sys.argv[0]
            u += '?url="'+urllib.quote_plus(video_id)+'"'
            u += '&mode="'+urllib.quote_plus(mode)+'"'
            u += '&videoid="'+urllib.quote_plus(common.args.videoid)+'"'
            u += '&pod="'+urllib.quote_plus(str(pod))+'"'
            u += '&guid="'+urllib.quote_plus(GUID)+'"'
            item=xbmcgui.ListItem("AD "+str(pod))
            item.setProperty('IsPlayable', 'true')
            common.playlist.add(url=u, listitem=item)
        return

    def MakeIV(self):
        data = common.makeGUID()
        data = binascii.unhexlify(data)
        return base64.encodestring(data).replace('\n','')

    def ADencrypt(self, data, iv):
        key = '9dbb5e376e65a64324e9269775dafd5b83c38f1d8819d5f1dc4ec2083c081bdb'
        cbc = common.AES_CBC(binascii.unhexlify(key))
        encdata = cbc.encrypt(data,base64.decodestring(iv))
        return base64.encodestring(encdata).replace('\n','')

    def ADdecrypt(self, data):
        key = '9d489e6c3adfb6a00a23eb7afc8944affd180546c719db5393e2d4177e40c77d'
        bindata = base64.decodestring(data)[1:]
        cbc = common.AES_CBC(binascii.unhexlify(key))
        return cbc.decrypt(bindata)

    def playAD(self, video_id, pod, GUID):
        if os.path.isfile(common.ADCACHE):
            data=common.OpenFile(common.ADCACHE)
            playlistSoup=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
            self.sstate = playlistSoup.find('sessionstate')['value']                                       
            self.ustate = playlistSoup.find('userstate')['value']
            del playlistSoup
            session=self.sstate
            state=self.ustate
        else:
            session=''
            state=''
        epoch = str(int(time.mktime(time.gmtime())))
        # token plid for plsnid
        if common.settings['enable_login'] =='true' and common.settings['usertoken']:
            UserID = common.settings['userid']
            if common.settings['planid'] == '' or common.settings['planid'] == None:
                PlanID = '0'
            else:
                PlanID = common.settings['planid']
        else:
            UserID = '-1'
            PlanID = '0'
        xmlbase='''
<AdRequest Pod="'''+str(pod)+'''" SessionState="'''+session+'''" ResponseType="VAST" Timestamp="'''+epoch+'''">
  <Distributor Name="Hulu" Platform="Desktop"/>
  <Visitor IPV4Address="" BT_RSSegments="null" UserId="'''+UserID+'''" MiniCount="" MiniDuration="" ComputerGuid="'''+GUID+'''" AdFeedback="null" PlanId="'''+PlanID+'''" FlashVersion="WIN 11,1,102,55" State="'''+state+'''"/>
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
        playlist = self.ADdecrypt(encplaylist)
        common.SaveFile(common.ADCACHE, playlist)
        playlistSoup=BeautifulStoneSoup(playlist, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        #print playlistSoup.prettify()
        self.sstate = playlistSoup.find('sessionstate')['value']                                       
        self.ustate = playlistSoup.find('userstate')['value']
        trackingurls = []
        stack = 'stack://'
        title = ''
        for ad in playlistSoup.findAll('ad'):
            mediafiles = ad.findAll('mediafile')
            if common.settings['adquality'] <= len(mediafiles):
                mediaUrl = mediafiles[common.settings['adquality']].string
            else:
                mediaUrl = mediafiles[0].string
            adtitle = ad.find('adtitle').string
            title += ' '+adtitle+''
            stack += mediaUrl.replace(',',',,')+' , '
        stack = stack[:-3]
        title = title.strip()
        item = xbmcgui.ListItem(title, path=stack)
        item.setInfo( type="Video", infoLabels={ "Title":title})
        xbmcplugin.setResolvedUrl(common.handle, True, item)
        for item in playlistSoup.findAll('tracking'):
            common.getFEED(item.string)