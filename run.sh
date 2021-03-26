#!/bin/bash

docker volume create --name=db-auth-volume
docker volume create --name=db-metrics-volume
docker volume create --name=db-tasks-volume
docker-compose build
docker-compose up