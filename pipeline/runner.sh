#!/bin/bash
export PATH="$(pwd):$PATH"
python3 download_s3_files.py
python3 Beiwe-Analysis/Pipeline/${FREQ}.py
