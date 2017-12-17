# Parent image
FROM ubuntu:16.04

# Install system requirements
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "python-pip", "python3-pip", "r-base"]

# Work from home directory
WORKDIR /home

# Move the directory into the corresponding directory in the container
ADD Beiwe-Analysis Beiwe-Analysis
ADD runner.sh runner.sh
ADD download_s3_files.py download_s3_files.py
ADD upload_s3_files.py upload_s3_files.py

# Install python and R requirements
RUN ["pip", "install", "--upgrade", "pip"]
RUN ["pip", "install", "-r", "Beiwe-Analysis/Pipeline/python2-requirements.txt"]
RUN ["pip3", "install", "--upgrade", "pip"]
RUN ["pip3", "install", "boto3==1.4.8", "requests==2.18.4"]
RUN ["pip3", "install", "-r", "Beiwe-Analysis/Pipeline/python3-requirements.txt"]
