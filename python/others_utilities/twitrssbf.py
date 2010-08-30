#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib2
import sys

class RSSFeeding:
	def __init__(self, userid, username):
		self.successpasswd = ''
		self.url = "http://twitter.com/statuses/user_timeline/" + userid + '.rss'
		print self.url
		self.username = username # I dont care about speed of parsing less strings because internet is too slow

	def tryget(self, pw):
		self.authhandler = urllib2.HTTPBasicAuthHandler()
		self.authhandler.add_password (realm='Twitter API', uri=self.url, user=self.username, passwd=pw)
		self.opener = urllib2.build_opener(self.authhandler)

		try:
			self.opener.open(self.url,None,1)
		except IOError, e:
			print e
			return 1
		else:
			return pw
		

if __name__ == '__main__':
	#attemptpri = RSSFeeding('/statuses/user_timeline/60787829.rss', 'prinewgirl')
	attemptleleo = RSSFeeding('14840601', 'leleobhz')
	# This shit works, but twitter locks account...