# AJK TODO not clear how exactly I want to do this. Options include:
# 1. have multiple Django apps
# B. make a single /models directory and put several X_models.py files in it, then have models.py call them all
# iii. keep everything in one models.py file (this seems like a bad idea)

from django.db import models


class ChunkRegistry(models.Model):
    pass


class FileToProcess(models.Model):
    pass

