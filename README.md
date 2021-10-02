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

## Build and push
> docker login
> docker build -t mojo1821/shinee-scraper:latest .
> docker push mojo1821/shinee-scraper:latest

## Now, this app is dockerized🎉
1. To execute, 
   * with production config,
    > docker compose --env-file .env.prod up -d
   * with development config,
    > docker compose up -d
2. To send SIGINT (stop program and send the recording to recipients)
    > docker kill --signal=SIGINT {container id}

## Useful docker compose commands
1. To rebuild after changing source codes,
    > docker compose up -d --build

## TODOs
0. Make this an web application.
   - Google drive, youtube, gmail notification must be retrieved by user interaction.
1. manage replica set to enhance availability
2. enhance observability (monitoring)

## Run Local (to get authenticated in console)
1. Run standalone chrome
> docker run -d -p 4444:4444 --shm-size="2g" mojo1821/standalone-chrome:latest
2. Add `127.0.0.1 chrome` to `/etc/hosts`
3. run
> python src/main.py
