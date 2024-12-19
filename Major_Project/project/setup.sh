#!/bin/bash

# Update package lists and install necessary packages
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
pip install -r requirements.txt
