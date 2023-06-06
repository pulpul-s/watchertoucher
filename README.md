# watchertoucher
Python watchdog script that looks for new/remove/move filesystem events on cifs/nfs/others and writes/removes a dummy file on it, so Jellyfin inotify implementation reacts  and scans the library for changes. This is a really bad, but working method of making Jellyfin real time monitoring to work on network filesystems, like cifs and nfs shares, and probably other unsupported filesystems.

## Usage
Change parameters on the script, run.<br>

You should set the folder variable as the parent folder that holds your media folders and the libraries as the actual media library folders. Watchdog will monitor the folder set as folder and react to changes made in folders provided in libraries array by touching a file in the root of the library folder in question.<br>

e.g. when folder is set as /mediaserver/ and libraries is set as "audio", it will monitor the whole mediaserver folder, but will only touch a file in the audio folder when changes are detected in it.<br>

touchdelay is implemented, so the script does not do needless writes when moving or saving large amounts of files at once to the same library. Jellyfin inotify implementation updates roughly after a minute from the touch. Setting it to 59 seconds *should* be safe.
>06.06.2023 **16:18:58** File created /mediaserver/libraries/video/test.mkv - touched /mediaserver/libraries/video/<br>
>[2023-06-06 **16:19:58**.733 +03:00] [INF] [39] Emby.Server.Implementations.IO.LibraryMonitor: "video" ("/media/video") will be refreshed.

Works at least with Python3.9 and Watchdog 3.0.0.
