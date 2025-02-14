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
-v {PATH_TO_CONFIG}:/config \
--restart unless-stopped \
jaymeswhyte/teemarr:latest
```
## Features & Commands
_This section is still in construction._
