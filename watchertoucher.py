#!/usr/bin/python3 -u

# watchertoucher 0.0.2
# https://github.com/pulpul-s/watchertoucher

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
## delay in seconds to write new touchfiles, use 0 to disable
touchdelay = 10
## files to ignore, don't remove the touchfile from the list
ignored_files = [touchfile]
## Watch the folder recusively True/False, do not change from True
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
        logentry = pvm + " File moved/renamed " + src + " " + "->" + " " + dest
    elif etype == "touch":
        logentry = src

    if logging == True:
        log = open(logfile, "a")
        log.write(logentry)
        log.close()
    else:
        print(logentry, end="")


lasttouch = [time.time() - touchdelay, ""]


def toucher(src, dest="", etype=""):
    # write and delete a dummy file to the root of the library
    global lasttouch
    for lib in libraries:
        if (
            (
                etype == "move"
                and os.path.dirname(dest).startswith(folder + lib)
                and lasttouch[0] + touchdelay <= time.time()
            )
            or (
                etype == "move"
                and os.path.dirname(dest).startswith(folder + lib)
                and lasttouch[1] != lib
            )
            or (
                os.path.dirname(src).startswith(folder + lib)
                and lasttouch[0] + touchdelay <= time.time()
            )
            or (os.path.dirname(src).startswith(folder + lib) and lasttouch[1] != lib)
        ):
            f = open(folder + lib + "/" + touchfile, "w")
            f.close()
            os.remove(folder + lib + "/" + touchfile)
            logger("touch", " - touched " + folder + lib + "/\n")
            lasttouch[0] = time.time()
            lasttouch[1] = lib
            return
        elif (
            lasttouch[0] + touchdelay > time.time()
            and os.path.dirname(src).startswith(folder + lib)
            or (
                etype == "move"
                and lasttouch[0] + touchdelay > time.time()
                and os.path.dirname(dest).startswith(folder + lib)
            )
        ):
            logger(
                "touch",
                f" - nothing touched, touched {lib} under {touchdelay} seconds ago\n",
            )
            return
    logger("touch", " - nothing touched\n")


class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(
            patterns=filetypes,
            ignore_patterns=ignored_files,
            ignore_directories=False,
            case_sensitive=False,
        )

    def on_created(self, event):
        try:
            logger("new", event.src_path)
            toucher(event.src_path)
        except Exception as e:
            print("Error in on_created:", str(e))

    def on_deleted(self, event):
        try:
            logger("del", event.src_path)
            toucher(event.src_path)
        except Exception as e:
            print("Error in on_deleted:", str(e))

    def on_moved(self, event):
        try:
            logger("move", event.src_path, event.dest_path)
            toucher(event.src_path, event.dest_path, "move")
        except Exception as e:
            print("Error in on_moved:", str(e))


if __name__ == "__main__":
    event_handler = Handler()
    observer = PollingObserver()
    observer.schedule(event_handler, path=folder, recursive=recur)
    observer.start()
    try:
        liblist = ""
        for index, lib in enumerate(libraries):
            if index == len(libraries) - 1:
                liblist += lib
            else:
                liblist += lib + ", "
        print(f"Watchertoucher 0.0.2 - watching {folder} and touching {liblist}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        pass
    finally:
        observer.stop()
        observer.join()
