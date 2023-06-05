# watchertoucher
Python watchdog script that looks for new/remove/move filesystem events on cifs/nfs/others and writes/removes a dummy file on it, so Jellyfin inotify implementation reacts to it and scans the library for new files. This is a really bad way of making Jellyfin real time monitoring to work on network filesystems, like cifs and nfs shares, and probably other unsupported filesystems.

## Usage
Change parameters on the script, run.
Works at least with Pytnon3.9 and Watchdog 3.0.0.
