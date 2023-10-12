FROM debian:11-slim
RUN apt update && apt install -y openjdk-17-jdk python3 python3-pip
WORKDIR /analysis/
COPY ./dependencies/ ./dependencies/
COPY ./config/ ./config/
COPY ./scripts/ ./scripts/
COPY ./run.sh ./
COPY ./iotflow.jar ./
COPY ./execute_iotflow.sh ./
RUN pip install -r /analysis/scripts/requirements.txt
