```
   _____ _     _                  _____                                
  / ____| |   (_)                / ____|                               
 | (___ | |__  _ _ __   ___  ___| (___   ___ _ __ __ _ _ __   ___ _ __ 
  \___ \| '_ \| | '_ \ / _ \/ _ \\___ \ / __| '__/ _` | '_ \ / _ \ '__|
  ____) | | | | | | | |  __/  __/____) | (__| | | (_| | |_) |  __/ |   
 |_____/|_| |_|_|_| |_|\___|\___|_____/ \___|_|  \__,_| .__/ \___|_|   
                                                      | |              
                                                      |_|              v1.0 by Danwoo Park
```

## Summary
ShineeScraper is an Afreeca TV live stream downloader.
Download afreeca live stream and upload it to Google drive, then send you an email so that you can watch it later anytime you want.

## Now, this app is dockerized🎉
1. To execute,
    > docker compose up -d
2. To send SIGINT (stop program and send the recording to recipients)
    > docker kill --signal=SIGINT {container id}

## TODOs
1. manage replica set to enhance availability
2. enhance observability (monitoring)
