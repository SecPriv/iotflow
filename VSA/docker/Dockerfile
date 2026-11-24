# Java 17 runtime, preinstalled (debian:11-slim can no longer install OpenJDK: its security repo is gone).
# Java 17 runs both the current vsa.jar (Soot 4.4.1) and the Soot 4.7.1 build; do not go above 17: the
# VSA stops runaway simulations with Thread.stop(), which throws on Java 20+.
FROM eclipse-temurin:17-jre
WORKDIR /vsa
COPY ./config/ ./config/
COPY ./execute_vsa.sh ./run.sh ./
# vsa.jar, android-31.jar, dex2jar and the instrumentation agent come from the shared top-level
# dependencies/ folder, mounted at /vsa/dependencies (see ../../compose.yaml).
# The container runs as the host user: let any user write its working files (JVM crash reports etc.)
RUN chmod 1777 /vsa
