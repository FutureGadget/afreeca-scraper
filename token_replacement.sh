#!/usr/bin/env bash

REMOTE_SERVER=lightsail
APP_NAME=shinee-scraper
USER=ec2-user
HOME=/home/${USER}
PROJECT_DIR=${HOME}/${APP_NAME}

rsync -av ./token ${REMOTE_SERVER}:${PROJECT_DIR}