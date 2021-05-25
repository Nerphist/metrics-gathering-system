#!/bin/bash

docker-compose down

docker volume rm user-photos-volume
docker volume rm documents-volume
docker volume rm db-auth-volume
docker volume rm db-metrics-volume
docker volume rm db-document-volume

docker volume create --name=user-photos-volume
docker volume create --name=documents-volume
docker volume create --name=db-auth-volume
docker volume create --name=db-metrics-volume
docker volume create --name=db-document-volume

docker-compose build
docker-compose --env-file .debug.env up