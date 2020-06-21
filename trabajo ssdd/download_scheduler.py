#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-
import Ice
import IceStorm
Ice.loadSlice("downloader.ice")
import Downloader
import work_queue
import binascii

class DownloadSchedulerI(Downloader.DownloadScheduler,Downloader.SyncEvent):

	def __init__(self,  name, sync_publisher, publisher_ProgressTopic):
		self.name = name
		self.SongList = set({})
		self.sync_publisher = sync_publisher
		self.publisher_ProgressTopic = publisher_ProgressTopic
		self.workqueue = work_queue.WorkQueue(self, self.publisher_ProgressTopic)
		self.workqueue.start()

	def requestSync(self,current = None):
		print("Sync() requested")
		self.sync_publisher.notify(list(self.SongList))

	def notify(self, songs,current = None):
		self.SongList=self.SongList.union(set(songs))


	def getSongList(self,current = None):
		return list(self.SongList)

	def addDownloadTask(self, url, current = None):
		self.workqueue.add(url)

	def get(self,song,current = None):
		transfer = TransferI("/tmp/{0}".format(song))
		proxy = current.adapter.addWithUUID(transfer)
		return Downloader.TransferPrx.checkedCast(proxy)

class TransferI(Downloader.Transfer):
    '''
    Transfer file
    '''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current = None):
        '''Send data block to client'''
        return str(
            binascii.b2a_base64(self.file_contents.read(size), newline = False)
        )

    def end(self, current = None):
        '''Close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)
