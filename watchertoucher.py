#!/usr/bin/python3 -u

# watchertoucher - a jellyfin media library refresher on network filesystem changes
# https://github.com/pulpul-s/watchertoucher
import time
import requests
import threading
import watchdog.events
from watchdog.observers.polling import PollingObserver
from datetime import datetime


# jellyfin url and port (str)
jellyfin_url = "http://127.0.0.1:8096"

# jellyfin api token, create one in the dashboard (str)
api_key = "your-api-key"

# parent folder for your media libraries (str)
mediafolder = "/mediaserver/libraries/"

# files to watch (str[List])
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
    "*.ogg",
    "*.flac",
    "*.m4a",
    "*.srt",
    "*.sub",
    "*.ass",
    "*.idx",
    "*.smi"
]

# list files to ignore, wildcards supported (str[List])
ignored_files = ["this.file", "that.file"]

# delay in seconds to prevent api spam if multiple files are created in a short period of time (int)
delay_seconds = 60

# logging messages to a file (bool)
log_to_file = True

# logging messages to stdout (bool)
log_to_stdout = False

# logfile location
logfile = "/var/log/watchertoucher.log"

# polling observer timeout in seconds, higher value
# means lower cpu usage and slower change detection (int)
po_timeout = 5

# timestamp format (str)
date_format = "%Y-%m-%d %H:%M:%S"


# functional variables
request_scheduled = False
scheduled_refresh_time = 0
lock = threading.Lock()
version = "0.1.0"


def log_message(message, end="\n"):
    timestamp = datetime.now().strftime(date_format)

    if end != "\n":
        formatted_message = f"{timestamp} {message}"
    else:
        formatted_message = f"{message}"

    if log_to_stdout:
        print(formatted_message + end)
    if log_to_file:
        with open(logfile, "a") as log:
            log.write(formatted_message + end)


def send_refresh_request():
    global request_scheduled, scheduled_refresh_time

    with lock:
        request_scheduled = True

    time.sleep(delay_seconds)

    headers = {"Authorization": f'MediaBrowser Token="{api_key}", Client="watchertoucher {version}"'}
    response = requests.post(f"{jellyfin_url}/Library/Refresh", headers=headers)

    with lock:
        request_scheduled = False
        scheduled_refresh_time = 0

    if response.status_code == 204:
        log_message("Jellyfin media library refresh request sent successfully\n", end="")
    elif response.status_code == 401:
        log_message("Failed to refresh Jellyfin library: 401 Unauthorized\n", end="")
    elif response.status_code == 403:
        log_message("Failed to refresh Jellyfin library: 403 Forbidden\n", end="")
    else:
        log_message(f"Failed to refresh Jellyfin library: {response.status_code} {response.text}\n", end="")


def queue_refresh():
    global request_scheduled, scheduled_refresh_time
    with lock:
        now = time.time()
        if request_scheduled and scheduled_refresh_time > now:
            remaining_time = int(scheduled_refresh_time - now)
            log_message(f", library refresh in {remaining_time} seconds")
            return

        scheduled_refresh_time = now + delay_seconds
        request_scheduled = True
        refresh_time_str = datetime.fromtimestamp(scheduled_refresh_time).strftime(date_format)

    threading.Thread(target=send_refresh_request, daemon=True).start()
    log_message(f", library refresh scheduled at {refresh_time_str}")


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
            log_message(f"File created: {event.src_path}", end="")
            queue_refresh()
        except Exception as e:
            log_message(f"Error in on_created: {str(e)}\n", end="")

    def on_deleted(self, event):
        try:
            log_message(f"File removed: {event.src_path}", end="")
            queue_refresh()
        except Exception as e:
            log_message(f"Error in on_deleted: {str(e)}\n", end="")

    def on_moved(self, event):
        try:
            log_message(f"File moved/renamed: {event.src_path} -> {event.dest_path}", end="")
            queue_refresh()
        except Exception as e:
            log_message(f"Error in on_moved: {str(e)}\n", end="")


if __name__ == "__main__":
    event_handler = Handler()
    observer = PollingObserver(timeout=po_timeout)
    observer.schedule(event_handler, path=mediafolder, recursive=True)
    observer.start()
    try:
        print(f"watchertoucher {version}, watching {mediafolder} and touching jellyfin api")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        observer.stop()
        observer.join()
