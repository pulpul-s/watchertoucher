#!/usr/bin/python3

import watchdog.events
import watchdog.observers
from watchdog.observers.polling import PollingObserver
import time
import os
from datetime import datetime

## files to watch
filetypes = [
    "*.mkv",
    "*.mp4",
    "*.avi",
    "*.m4v",
    "*.mov",
    "*.ts",
    "*.vob",
    "*.webm",
    "*.mp3",
    "*.mp2",
    "*.flac",
    "*.m4a",
]
## log changes to a file True/False
logging = False
## logfile location/name
logfile = "/mediaserver/filechanges.log"
## watched folder for changes
folder = "/mediaserver/videos/"
## dummy filename
touchfile = "watchertoucher.toucher"
## files to ignore, don't remove the touchfile from the list
ignored_files = [touchfile]
## Watch the folder recusively True/False
recur = True


def logger(etype, src, dest=None):
    now = datetime.now()
    pvm = now.strftime("%d.%m.%Y %H:%M:%S")

    if etype == "new":
        logentry = pvm + " New file " + src + "\n"
    elif etype == "del":
        logentry = pvm + " Removed file " + src + "\n"
    elif etype == "move":
        logentry = (
            pvm + " Moved or renamed file " + src + " " + "->" + " " + dest + "\n"
        )

    if logging == True:
        log = open(logfile, "a")
        log.write(logentry)
        log.close()
    else:
        print(logentry, end="")


def toucher():
    # write and delete a dummy file to trigger inotify
    f = open(folder + touchfile, "w")
    f.close()
    os.remove(folder + touchfile)


class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(
            self,
            patterns=filetypes,
            ignore_patterns=ignored_files,
            ignore_directories=False,
            case_sensitive=False,
        )

    def on_created(self, event):
        toucher()
        logger("new", event.src_path)

    def on_deleted(self, event):
        toucher()
        logger("del", event.src_path)

    def on_moved(self, event):
        toucher()
        logger("move", event.src_path, event.dest_path)


if __name__ == "__main__":
    event_handler = Handler()
    observer = PollingObserver()
    observer.schedule(event_handler, path=folder, recursive=recur)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
