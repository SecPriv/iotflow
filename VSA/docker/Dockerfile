# Java 17 runtime (the VSA uses FlowDroid 2.15.1 / Soot 4.7.1, which require Java 17)
FROM eclipse-temurin:17-jre
WORKDIR /vsa
COPY ./dependencies/ ./dependencies/
COPY ./config/ ./config/
COPY ./vsa.jar ./
COPY ./execute_vsa.sh ./run.sh ./
