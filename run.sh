#!/bin/bash
docker run -it --rm -v ./.env:/app/.env -v ./endpoints.txt:/app/endpoints.txt --env-file .env simple-endpoint-monitor-cli:0.0.1
