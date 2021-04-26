#!/bin/bash

docker-compose down

docker volume rm db-auth-volume
docker volume rm db-metrics-volume
docker volume rm db-tasks-volume

docker volume create --name=db-auth-volume
docker volume create --name=db-metrics-volume
docker volume create --name=db-tasks-volume

docker-compose build
docker-compose --env-file .debug.env up