module downloader{
	sequence<string>SongList;
	enum Status{Pending,Inprogress,Done,Error};
	struct ClipData{
	string URL;
	Status status;
	}
	exception SchedulerAlreadyExists{};
	exception SchedulerNotFound{};
	exception SchedulerCanalJob{};
	interface  Transfer{
		string recv(int size);
		void end();
	};
	interface DownloadScheduler{
		SongList getSongList();
		["and","ami" void  add DownloadTask(stringurl)]throwsSchedulerCanalJob;
		void canalTask(string url);
	};
	interface Scheduler Factory{
		DownloadScheduler*mak(string name) throws SchedulerAlredyExist;
		void kill(string name)throws SchedulerNotFound;
		int avalibleSchedulers();
	};
	interface ProgressEvent{
		void notify(clipData clipData);
	};
	interface SyncEvent{
		void requestSync();
		void notify(SongList songs);
	};
};