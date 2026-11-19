# Java 11 runtime, preinstalled (debian:11-slim can no longer install OpenJDK: its security repo is gone)
FROM eclipse-temurin:11-jre
WORKDIR /vsa
COPY ./dependencies/ ./dependencies/
COPY ./config/ ./config/
COPY ./vsa.jar ./
COPY ./execute_vsa.sh ./run.sh ./
