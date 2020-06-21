#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-
import sys
import Ice
import IceStorm
Ice.loadSlice("downloader.ice")
import Downloader
import download_scheduler

SYNCTOPIC = "SyncTopic"
PROGRESSTOPIC = "ProgressTopic"
ICESTORM_MANAGET = 'Downloader.IceStorm' #queda mas codigo que poner

class Scheduler_factoryI(Downloader.SchedulerFactory):
	def __init__(self,SyncTopic,sync_publisher, publisher_ProgressTopic):
		self.SyncTopic = SyncTopic
		self.registry = {}
		self.sync_publisher = sync_publisher
		self.publisher_ProgressTopic = publisher_ProgressTopic


	def make(self,name,current = None):
		if name in self.registry:
			raise Downloader.SchedulerAlreadyExists

		scheduler = download_scheduler.DownloadSchedulerI(name,self.sync_publisher, self.publisher_ProgressTopic)
		scheduler_proxy = current.adapter.add(scheduler,Ice.stringToIdentity(name))
		qos = {}
		self.SyncTopic.subscribeAndGetPublisher(qos,scheduler_proxy)
		self.registry[name] = scheduler_proxy
		return Downloader.DownloadSchedulerPrx.checkedCast(scheduler_proxy)

	def kill(self, name, current = None):
		if name not in self.registry:
			raise Downloader.SchedulerNotFound

		current.adapter.remove(Ice.stringToIdentity(name))
		self.SyncTopic.unsubscribe(self.registry[name])
		del(self.registry[name])

	def availableSchedulers(self,curret = None):
		return len(self.registry)

class Server(Ice.Application):
	def get_topic_manager(self):
		key = 'IceStorm.TopicManager.Proxy'
		proxy = self.communicator().propertyToProxy(key)
		if proxy is None:
			print("property '{}' not set".format(key))
			return None

		print("Using IceStorm in: '%s'" % key)
		return IceStorm.TopicManagerPrx.checkedCast(proxy)

	def run(self, argv):
		topic_mgr = self.get_topic_manager()
		broker = self.communicator()
		factory_adapter = broker.createObjectAdapter("FactoryAD")

		if not topic_mgr:
			print("Invalid proxy")
			return 2
		qos = {}
		try:
			topic = topic_mgr.retrieve(SYNCTOPIC)
		except IceStorm.NoSuchTopic:
			topic = topic_mgr.create(SYNCTOPIC)

		publisher_SyncTime = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())

		qos2 = {}

		try:
			ProgressTopic = topic_mgr.retrieve(PROGRESSTOPIC)
		except IceStorm.NoSuchTopic:
			ProgressTopic = topic_mgr.create(PROGRESSTOPIC)

		publisher_ProgressTopic = Downloader.ProgressEventPrx.uncheckedCast(ProgressTopic.getPublisher())

		factory = Scheduler_factoryI(topic, publisher_SyncTime, publisher_ProgressTopic)
		factory_proxy = factory_adapter.add(factory, Ice.stringToIdentity("Factory1"))
		print(factory_proxy)

		factory_adapter.activate()
		self.shutdownOnInterrupt()
		broker.waitForShutdown()

		return 0
if __name__ == '__main__':
	APP = Server()
	sys.exit(APP.main(sys.argv))
