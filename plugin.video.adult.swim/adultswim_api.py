#!/usr/bin/python

import urllib, urllib2, re, md5
import string, os, time, datetime
from elementtree.ElementTree import *

CONFIGURATION_URL = "http://asfix.adultswim.com/staged/configuration.xml"
SERVER_TIME_URL = "http://asfix.adultswim.com/asfix-svc/services/getServerTime"
EPISODES_BY_SHOW_URL = "http://asfix.adultswim.com/asfix-svc/episodeSearch/getEpisodesByShow?id=%s&filterByEpisodeType=%s&networkName=AS"
EPISODES_BY_IDS_URL = "http://asfix.adultswim.com/asfix-svc/episodeSearch/getEpisodesByIDs?ids=%s&networkName=AS"

class AdultSwim(object):
	def __init__(self):
		return
		

	def getCategories(self):
		response = self._request( CONFIGURATION_URL )
		xml = ElementTree(fromstring(response))
		categories = []
		for cat in xml.getroot().findall('logiccategories/category'):
			category = {
				'name': cat.get('name'),
				'id': cat.get('categoryId'),
				'description': cat.get('description')
			}
			categories.append( category )
		
		return categories
	
	def getShowsByCategory(self, id):
		response = self._request( CONFIGURATION_URL )
		xml = ElementTree(fromstring(response))
		shows = []
		for cat in xml.getroot().findall("logiccategories/category"):
			if(cat.get('categoryId') == id):
				for sh in cat.findall('collection'):
					show = {
						'name':sh.get('name'),
						'id':sh.get('id')
					}
					shows.append( show )
				break
		
		return shows
	
	
	def getEpisodesByShow(self, id, filter):
		response = self._request( EPISODES_BY_SHOW_URL % (id, filter) )
		xml = ElementTree(fromstring(response))
		episodes = []
	
		for ep in xml.getroot().findall('episode'):
                        episode = {
                                        'title': ep.get('title'),
                                        'collectionTitle': ep.get('collectionTitle'),
                                        'id': ep.get('id'),
                                        'showId': ep.get('showId'),
                                        'thumbnail': ep.get('thumbnailUrl'),
                                        'category': ep.get('collectionCategoryType'),
                                        'episodeNumber': ep.get('episodeNumber'),
                                        'epiSeasonNumber': ep.get('epiSeasonNumber'),
                                        'rating': ep.get('rating'),
                                        'ranking': ep.get('ranking'),
                                        'views': ep.get('numberOfViews'),
                                        'language': ep.get('language'),
                                        'expirationDate': ep.get('expirationDate'),
                                        'episodeType': ep.get('episodeType'),
                                        'collectionCategoryType': ep.get('collectionCategoryType'),
                                        'description': ep.find('description').text.replace('&apos;',"'").replace('&quot;','"'),
                                        'segments':[]
                                        }
			for seg in ep.findall('segment'):
				segment = {
					'id': seg.get('id'),
					'thumbnail': seg.get('thumbnailUrl')
				}
				episode['segments'].append( segment )
	
			episodes.append( episode )
			
		return episodes

	
	
	def getEpisodesByIDs(self, ids):
	
		response = self._request( EPISODES_BY_IDS_URL % (ids) )
		xml = ElementTree(fromstring(response))

		episodes = []
		for ep in xml.getroot().findall('episode'):
			episode = {
				'title': ep.get('title'),
				'collectionTitle': ep.get('collectionTitle'),
				'id': ep.get('id'),
				'showId': ep.get('showId'),
				'thumbnail': ep.get('thumbnailUrl'),
				'category': ep.get('collectionCategoryType'),
                                'episodeNumber': ep.get('episodeNumber'),
                                'epiSeasonNumber': ep.get('epiSeasonNumber'),
				'rating': ep.get('rating'),
				'ranking': ep.get('ranking'),
				'views': ep.get('numberOfViews'),
				'language': ep.get('language'),
				'expirationDate': ep.get('expirationDate'),
				'episodeType': ep.get('episodeType'),
				'collectionCategoryType': ep.get('collectionCategoryType'),
				'description': ep.find('description').text.replace('&apos;',"'").replace('&quot;','"'),
				'segments':[]
			}
			for seg in ep.findall('segments/segment'):
				print seg.get('id')
				segment = {
					'id': seg.get('id'),
					'thumbnail': seg.get('thumbnailUrl')
				}
				episode['segments'].append( segment )
	
			episodes.append( episode )
			
		return episodes
	
	
	
	
	
	def getServerTime(self):
		response = self._request( SERVER_TIME_URL )
		xml = ElementTree(fromstring(response))
		return xml.getroot().text

        def getPlaylist(self, pid):
                try:
                        getVideoPlaylist    = 'http://asfix.adultswim.com/asfix-svc/episodeservices/getVideoPlaylist'
                        url = getVideoPlaylist + '?id=' + pid + '&r=' + self.getServerTime()
                        print 'Adult Swim --> getplaylist :: url = '+url
                        stime = self.getServerTime()
                        token = stime + '-' + md5.new(stime + pid + '-22rE=w@k4raNA').hexdigest()
                        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
                                   'Host': 'asfix.adultswim.com',
                                   'Referer':'http://www.adultswim.com/video/ASFix.swf',
                                   'x-prefect-token': token
                                   }
                        req = urllib2.Request(url,'',headers)    
                        response = urllib2.urlopen(req)
                        link=response.read()
                        response.close()
                except urllib2.URLError, e:
                        print 'Error code: ', e.code
                        return False
                else:
                        return link
                
	
	def _request(self, url, data=None, token=None):
                print url
		headers = { 
			'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
			'Referer':'http://www.adultswim.com/video/ASFix.swf'
		}
		if data:
			data = urllib.urlencode(data)
		if token:
			headers['x-prefect-token'] = token
		req = urllib2.Request(url, data, headers)
		response = urllib2.urlopen(req)
		the_page = response.read()
		response.close()
		return the_page
