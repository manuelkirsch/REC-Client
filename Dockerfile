# Dockerfile, Image, Container
FROM python:3.9.18-slim-bullseye

ADD forward.py .

# openwakeword is used for wakeword detection
# samplerate is used for down/upsampling the microphone stream to 16kHz because openwakeword works best with 16kHz
# paho-mqtt is used for sending results to mqtt server

RUN pip install websocket-client rel paho-mqtt

CMD ["python", "./forward.py"]

# build image with: docker build -t python-magichome .