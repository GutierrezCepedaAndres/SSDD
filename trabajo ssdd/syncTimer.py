#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-

import sys
import time
import Ice
import IceStorm
Ice.loadSlice("downloader.ice")
import Downloader

key = "IceStorm.TopicManager.Proxy"
topic_name = "SyncTopic"


class Publisher(Ice.Application):

	def get_topic_manager(self):
		proxy = self.communicator().propertyToProxy(key)
		if proxy is None:
			print( "property", key,"not set")
			return None

		print("Using IceStorm in: '%s'"% key)
		return IceStorm.TopicManagerPrx.checkedCast(proxy)

	def run(self,argv):
		broker = self.communicator()
		#Get topic manager
		topic_mgr_proxy = self.communicator().propertyToProxy(key)

		if(topic_mgr_proxy is None):
			print("Property {0} not set".format(key))
		topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
		if not topic_mgr:
			print ("invalid proxy")
			return 2

		#Get topic
		try:
			topic = topic_mgr.retrieve(topic_name)
		except IceStorm.NoSuchTopic:
			topic = topic_mgr.create(topic_name)

		publisher = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())

		#Shot event
		while True:
			print ("Sending Sync() request")
			publisher.requestSync()
			time.sleep(5.0)

		#Bye
		return 0

if __name__ == '__main__':
    server = Publisher()
    sys.exit(server.main(sys.argv))
