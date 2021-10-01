#!/usr/bin/env bash
ENV_FILE=.env
REMOTE_SERVER=lightsail
APP_NAME=afreeca-scraper
PROJECT_DIR=~/project/${APP_NAME}
DOCKER_COMPOSE_FILE_PATH=${PROJECT_DIR}/${APP_NAME}/docker-compose.yml
# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} down"
# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "rm -rf ${PROJECT_DIR}"
scp -r . ${REMOTE_SERVER}:${PROJECT_DIR}
# shellcheck disable=SC2029
ssh ${REMOTE_SERVER} "docker-compose -f ${DOCKER_COMPOSE_FILE_PATH} --env-file=${ENV_FILE} up -d --build"
ssh ${REMOTE_SERVER} "docker ps"
