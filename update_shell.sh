#!/usr/bin/env bash
REMOTE_SERVER=sc
APP_NAME=afreeca-scraper
USER=ec2-user
HOME=/home/${USER}
PROJECT_DIR=${HOME}/${APP_NAME}

ENV='prod'

### Manual sync ###

rsync -av ./src ${REMOTE_SERVER}:${PROJECT_DIR}
