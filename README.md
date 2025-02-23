# Teemarr (WIP)
*A self-hosted, containerised discord bot to help manage your Plex media server.*
## Installation
_DockerHub_ page [here](https://hub.docker.com/r/jaymeswhyte/teemarr).
Use the following command:
```
docker run -d \
--name=teemarr \
-e PUID=1000 \
-e PGID=1000 \
-e TZ=Eire \
-e TOKEN={DISCORD_BOT_TOKEN} \
-e GUILD_ID={YOUR_GUILD_ID} \
-e QBIT_USER={BITTORRENT_USERNAME} \
-e QBIT_PASS={QBITTORRENT_PASS} \
-e QBIT_ADDRESS={QBITTORRENT_IP} \
-e QBIT_PORT=8080 \
-e OVERSEERR_KEY={OVERSEERR_KEY} \
-e OVERSEERR_ADDRESS={OVERSEER_IP} \
-e OVERSEERR_PORT=5055 \
-e NOTIFICATION_CHANNEL=notifications \
-e STATUS_CHANNEL=status \
-e WEBHOOK_PORT=5000 \
-p 5000:5000 \
-v {PATH_TO_CONFIG}:/config \
--restart unless-stopped \
jaymeswhyte/teemarr:latest
```
## Why Teemarr?
Teemarr allows you and your friends to manage your media server stack remotely, without the use of any tunelling or VPN connection!

## Commands & Features 
### Content Management
#### `/request {title}`
- Searches for the given title and returns a list of options as button embeds
- Selected title is logged as a request with Overseerr
- Ideally, Overseerr should be set to automatically accept requests
- Requests stored in a local TinyDB database

### Torrent Management
#### `/torrentlist`
- Responds with a list of all active torrents, detailing title, status, seed count and progress
#### `/pause`
- Pause all active torrents (helpful for scenarios with limited bandwidth)
#### `/resume`
- Resume all active torrents

### Bot Configuration and Debugging
#### `/echo {msg}`
- Echo the given message; Useful to verify server is online and bot is running
#### `/overnights {setting}`
- Configure overnight downloads with ON/OFF
- All torrents will pause at 08:00 and resume at 01:00
- Helpful for scenarios with limited bandwidth

### New Title Notifications
- Plex webhooks can be set to notify Teemarr of new titles
- Teemarr listens on port 5000 (by default) at the endpoint `/webhook`
- If the new title was requested via Teemarr, the user who requested it will be pinged

## Future Features (1.0 release)
As this is a work in progress side project, not all planned features have yet been implemented. Some planned future features include:

- Pausing/Resuming of specific torrents
- Season-specific series requests
- Selectable quality profiles
- Configurable overnight download times
- ...Etc
