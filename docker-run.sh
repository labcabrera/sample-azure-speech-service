#!/bin/bash

docker stop azure-speech-api

docker build -t azure-speech-api .

docker run --rm -p 8000:8000 -e SPEECH_KEY="$SPEECH_KEY" -e SPEECH_REGION="$SPEECH_REGION" azure-speech-api
