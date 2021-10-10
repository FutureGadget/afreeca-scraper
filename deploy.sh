#!/usr/bin/env bash
REMOTE_SERVER=lightsail
APP_NAME=shinee-scraper
USER=ec2-user
HOME=/home/${USER}
PROJECT_DIR=${HOME}/${APP_NAME}
DOCKER_COMPOSE_FILE_PATH=${PROJECT_DIR}/docker-compose.yml

ENV_FILE=${PROJECT_DIR}/.env

# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} down"

# shellcheck disable=SC2029
#ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} --env-file=${ENV_FILE} up -d --build"
#ssh ${REMOTE_SERVER} "docker ps"

### Manual execute and build script ###
ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} down"

rsync -av ./configs ${REMOTE_SERVER}:${PROJECT_DIR}
rsync -av ./logs ${REMOTE_SERVER}:${PROJECT_DIR}
rsync -av ./secrets ${REMOTE_SERVER}:${PROJECT_DIR}
rsync -av ./token ${REMOTE_SERVER}:${PROJECT_DIR}
rsync -av ./videos ${REMOTE_SERVER}:${PROJECT_DIR}

# Dev
ssh lightsail "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} --env-file=${PROJECT_DIR}/.env up -d --build"
# Prod
ssh lightsail "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} --env-file=${PROJECT_DIR}/.env.prod up -d --build"