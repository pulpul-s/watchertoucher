# watchertoucher
Python `watchdog` script that monitors filesystem events (create, delete, move) on network-mounted drives (CIFS, NFS, etc.) and triggers a library refresh on a Jellyfin server.

By default, it schedules the refresh one minute into the future, avoiding API spam when multiple filesystem changes occur in a short time window.


## Requirements

- Python 3.6+
- `watchdog` for filesystem monitoring
- `requests` for jellyfin api calls


## Usage
```bash
pip install watchdog requests
```

Change at least `jellyfin_url`,`api_key` and `mediafolder` parameters on the script, run.<br>
You should set the `mediafolder` variable as the parent folder that holds your media folders.
Python Watchdog will monitor the folder recusively and react to changes made in it.<br><br>
Jellyfin API key can be created in `Settings -> Dashboard -> API Keys`

```bash
./watchertoucher.py
```



## Changelog

### watchertoucher 0.1.0:
- Rewrite of the script logic to use Jellyfin API instead of fooling Linux inotify
- Simplified and cleaned up the script behavior