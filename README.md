# Afreeca Live Stream Downloader
## Summary
Download afreeca live stream and upload it to Google drive, then send you an email so that you can watch it later.

## Now, this app is dockerized🎉
1. Forget the prerequisites above.
2. To execute,
    > docker compose up -d
3. To send SIGINT (stop program and send the recording to recipients)
    > docker kill --signal=SIGINT {container id}

## TODOs
1. manage replica set to enhance availablity
2. enhance observability (monitoring)
3. clean up `videos/` dir periodically.