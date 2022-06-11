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

# How to execute this program?
1. You should configure which BJ this program should monitor. When the BJ starts streaming, the recording will be started automatically. Only 1 BJ can be monitored at a time.
2. Google API secret json file is needed and properly located.
3. Youtube and gmail token should be set.
4. Necessary directories should be made in advance.
  - token/youtube
  - secrets
  - logs
  - videos

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
   - Should be able to retry upload manually after manually refreshing token.
1. manage replica set to enhance availability
2. enhance observability (monitoring)

## Run Local (to get authenticated in console)
### Using standalone-chrome with chromedriver docker image and local python
Make sure that the `type` is set to `REMOTE` under the `Selenium` config in the `configs/app_config-{env}.ini` file.
1. Run standalone chrome  
    `docker run -d -p 4444:4444 --shm-size="2g" mojo1821/standalone-chrome:latest`
2. Add `127.0.0.1 chrome` to `/etc/hosts`
3. create venv  
    `python -m venv shinee-scraper`
4. resolve dependencies  
    `pip install -r requirements.txt`
5. run  
    `python src/main.py`

### Using LOCAL chromedriver and LOCAL chrome and local python
Make sure that the `type` is set to `LOCAL` under the `Selenium` config in the `configs/app_config-{env}.ini` file.
Make sure that the `location` is set to a local `chromedriver` absolute path under the `Selenium` config in the `configs/app_config-{env}.ini` file.
Make sure that the `chrome` is installed on the same machine you run this program.
1. create venv  
    `python -m venv shinee-scraper`
2. resolve dependencies  
    `pip install -r requirements.txt`
3. run  
    `python src/main.py`


### Using docker-compose
Make sure that both `standalone-chrome` and `shinee-scraper` images are built and ready to run.
Make sure that the necessary directories exist in the binding volume.
Run docker compose and enjoy.

# Appedix
## How to install chrome binary?
### RHEL/CentOS
`wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm`  

`sudo yum install google-chrome-stable_current_x86_64.rpm`

> https://www.lesstif.com/lpt/linux-chrome-106857342.html

### WSL2 ubuntu
`sudo apt update && sudo apt -y upgrade && sudo apt -y autoremove`

`wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb`

`sudo apt -y install ./google-chrome-stable_current_amd64.deb`

`google-chrome --version`

> https://scottspence.com/posts/use-chrome-in-ubuntu-wsl
