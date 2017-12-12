# Parent image
FROM ubuntu:16.04

# Install necessaries
# TODO install R
RUN apt-get update && apt-get install -y python

# Work from home directory
WORKDIR ~

# Move the directory into the corresponding directory in the container
ADD Beiwe-Analysis Beiwe-Analysis
ADD runner.sh runner.sh
