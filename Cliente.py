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




class Cliente(Ice.Application):

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
            return topic
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create("ProgressTopic")
            return topic

        proxy_factory = self.communicator().stringToProxy(argv[1])
        factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy_factory)

        #adapter = self.communicator().createObjectAdapter("ProgressAdapter")

        print("Creamos un scheduler")
        factory.make("scheduler1")
        print("Mandamos url a download")
        factory.begin_addDownloadTask("https://www.youtube.com/watch?v=MocF43ncu8I")

        print("dormimos para espear a la descarga")
        time.sleep(2.0)

        print("Pedimos la lista de canciones")
        lista = factory.getSongList()
        print(lista)

        print("hacemos get del song {}".format(lista[0]))

        factory.get(str(lista[0]))

        print("Obtenemos el numero de schedulers disponibles")
        print(factory.availableSchedulers())

        print("Eliminamos el scheduler creado")
        factory.kill("scheduler1")

        print("Obtenemos el numero de schedulers disponibles")
        print(factory.availableSchedulers())


if __name__ == '__main__':
    APP = Cliente()
    sys.exit(APP.main(sys.argv))
