# Debian 12 with Python 3.9 (same Python as the original Debian 11 image, so the pinned requirements still install)
FROM python:3.9-slim-bookworm
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /analysis/
# Install Python dependencies first, so changes to scripts/configs don't trigger a reinstall
COPY ./scripts/requirements.txt ./scripts/requirements.txt
RUN pip install --no-cache-dir -r ./scripts/requirements.txt
COPY ./config/ ./config/
COPY ./iotflow.jar ./
COPY ./scripts/ ./scripts/
COPY ./run.sh ./execute_iotflow.sh ./
# vsa.jar (IoTScope), android-31.jar and dex2jar come from the shared top-level dependencies/ folder,
# mounted at /analysis/dependencies (see ../../compose.yaml).
# The container runs as the host user: let any user write its working files (sootOutput/, crash reports)
RUN chmod 1777 /analysis
