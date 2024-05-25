#!/bin/bash

# Check if .env file exists
if [ -f .env ]; then
  # Read and export variables from .env file
  export $(cat .env | xargs)
fi

# Publish using Poetry
poetry publish --username $PYPI_USERNAME --password $PYPI_PASSWORD --build
