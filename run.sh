#!/bin/sh
set -eu
docker build -t friend-reminder .
docker run -p 8080:8080 --env-file .env -v $(pwd)/db:/db friend-reminder
