FROM debian:11-slim
RUN apt update && apt install -y openjdk-11-jdk
WORKDIR /vsa
COPY ./dependencies/ ./dependencies/
COPY ./config/ ./config/
COPY ./execute_vsa.sh ./
COPY ./run.sh ./
COPY ./vsa.jar ./
