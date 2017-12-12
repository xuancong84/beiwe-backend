#!/bin/bash
# TODO this needs a bunch of changes to figure out the object_id and get S3 files
# Most of that should be done in python. I just need to pass the environment variables
export PATH="$(pwd):$PATH"
/bin/bash Beiwe-Analysis/Pipeline/$1.sh
