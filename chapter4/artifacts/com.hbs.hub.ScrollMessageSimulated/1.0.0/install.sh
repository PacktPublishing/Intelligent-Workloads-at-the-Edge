#!/bin/bash

sudo usermod -a -G i2c,video ggc_user 
sudo apt update
sudo apt upgrade -y
sudo apt install python3 libatlas-base-dev -y 
python3 -m venv env
env/bin/python -m pip install -r requirements.txt