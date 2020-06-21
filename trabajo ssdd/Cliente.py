#!/usr/bin/python3

import binascii
import sys
import time
import Ice
import IceStorm
#pylint: disable = E0401
#pyliny: disable = C0413
#pylint: disable = E1101
Ice.loadSlice('downloader.ice')
import Downloader

BLOCK_SIZE = 10240

class Cliente(Ice.Application):

    def receive(self,transfer, destination_file):
        '''
        Read a complete file using a Downloader.Transfer object
        '''
        with open(destination_file, 'wb') as file_contents:
            remoteEOF = False
            while not remoteEOF:
                data = transfer.recv(BLOCK_SIZE)
                # Remove additional byte added by str() at server
                if len(data) > 1:
                    data = data[1:]
                data = binascii.a2b_base64(data)
                remoteEOF = len(data) < BLOCK_SIZE
                if data:
                    file_contents.write(data)
            transfer.end()

    def run(self,argv):

        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)

        if proxy is None:
            print("property", key, "not set")
            return None

        # print("Using IceStorm in: '%s'" % key)
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(proxy)

        if not topic_mgr:
            print(': invalid proxy')
            return 2
        try:
            topic = topic_mgr.retrieve("ProgressTopic")
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create("ProgressTopic")

        proxy_factory = self.communicator().stringToProxy(argv[1])
        factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)

        #adapter = self.communicator().createObjectAdapter("ProgressAdapter")

        try:
            factory.kill("scheduler1")
        except:
            print("inicio")

        print("Creamos un scheduler")
        print("\nfactory.make(scheduler1\n)")

        scheduler = factory.make("scheduler1")
        print("Mandamos url a download")
        print("\nscheduler.begin_addDownloadTask(https://www.youtube.com/watch?v=MocF43ncu8I)\n")
        scheduler.begin_addDownloadTask("https://www.youtube.com/watch?v=MocF43ncu8I")

        print("Esperamos a que se descargue")
        while True:
            lista = scheduler.getSongList()
            if len(lista) is not 0:
                break

        print("Pedimos la lista de canciones")
        print("\nlista = scheduler.getSongList()\n")
        lista = scheduler.getSongList()
        print(lista)

        print("hacemos get del song {}".format(lista[0]))
        print("\ntransfer = scheduler.get(str(lista[0]))")
        print("\nself.receive(transfer,./{0}.format(lista[0]))\n")
        transfer = scheduler.get(str(lista[0]))
        self.receive(transfer,"./{0}".format(lista[0]))


        print("Obtenemos el numero de schedulers disponibles")
        print("\nprint(factory.availableSchedulers())\n")
        print(factory.availableSchedulers())

        print("Eliminamos el scheduler creado")
        print("\nfactory.kill(scheduler1)\n")
        factory.kill("scheduler1")

        print("Obtenemos el numero de schedulers disponibles")
        print("\nprint(factory.availableSchedulers())\n")
        print(factory.availableSchedulers())


if __name__ == '__main__':
    APP = Cliente()
    sys.exit(APP.main(sys.argv))
