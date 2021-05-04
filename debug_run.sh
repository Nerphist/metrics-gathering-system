#!/bin/bash

docker-compose build
docker-compose --env-file .debug.env up