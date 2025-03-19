#!/bin/sh

docker run -p 8000:8000 -v $(pwd):/app --name web-app -d flask-app