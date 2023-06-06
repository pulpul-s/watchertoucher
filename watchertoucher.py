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
## watched folder for changes (this should be the parent directory of your actual media library folders)
folder = "/mediaserver/libraries/"
## libraries in watched folder
libraries = ["video", "audio"]
## dummy filename
touchfile = "watchertoucher.toucher"
## files to ignore, don't remove the touchfile from the list
ignored_files = [touchfile]
## Watch the folder recusively True/False
recur = True
## log changes to a file True/False
logging = False
## logfile location/name
logfile = "/var/log/watchertoucher.log"


def logger(etype, src, dest=None):
    now = datetime.now()
    pvm = now.strftime("%d.%m.%Y %H:%M:%S")

    if etype == "new":
        logentry = pvm + " File created " + src
    elif etype == "del":
        logentry = pvm + " File removed " + src
    elif etype == "move":
        logentry = pvm + " File moved or renamed " + src + " " + "->" + " " + dest
    elif etype == "touch":
        logentry = src

    if logging == True:
        log = open(logfile, "a")
        log.write(logentry)
        log.close()
    else:
        print(logentry, end="")


def toucher(src, etype=None):
    # write and delete a dummy file to the root of the library
    for lib in libraries:
        if os.path.dirname(src).startswith(folder + lib):
            f = open(folder + lib + "/" + touchfile, "w")
            f.close()
            os.remove(folder + lib + "/" + touchfile)
            logger("touch", " - touched " + folder + lib + "/\n")
            return
    logger("touch", " - not touched\n")


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
        toucher(event.src_path)
        logger("new", event.src_path)

    def on_deleted(self, event):
        toucher(event.src_path)
        logger("del", event.src_path)

    def on_moved(self, event):
        toucher(event.src_path)
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
