#!/usr/bin/env bash
REMOTE_SERVER=lightsail
APP_NAME=afreeca-scraper
PROJECT_DIR=project/${APP_NAME}
DOCKER_COMPOSE_FILE_PATH=${PROJECT_DIR}/${APP_NAME}/docker-compose.yml

ENV_FILE=${PROJECT_DIR}/.env

# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} down"
# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "rm -rf ${PROJECT_DIR}"
# shellcheck disable=SC2029
rsync -av ./ lightsail:${PROJECT_DIR}

# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} --env-file=${ENV_FILE} up -d --build"
ssh ${REMOTE_SERVER} "docker ps"


### Manual execute and build script ###
ssh lightsail "docker-compose -f project/afreeca-scraper/docker-compose.yml down"
ssh lightsail "rm -rf project/afreeca-scraper"
rsync -av ./ lightsail:~/project/afreeca-scraper

# Dev
ssh lightsail "docker-compose -f project/afreeca-scraper/docker-compose.yml --env-file=project/afreeca-scraper/.env up -d --build"
# Prod
ssh lightsail "docker-compose -f project/afreeca-scraper/docker-compose.yml --env-file=project/afreeca-scraper/.env.prod up -d --build"