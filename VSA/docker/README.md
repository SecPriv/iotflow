# Docker Setup for VSA

## Steps 
1. add `apk` files to the folder `apps_to_analyze/`
2. `docker compose up`
3. Results will be placed into `results/`

## Configuration
* Edit `execute_vsa.sh` to change configuration values like timeouts (), maximum memory available to java, cut off values
* Edit config files to analyze different parameters and methods