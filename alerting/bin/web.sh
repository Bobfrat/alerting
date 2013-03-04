#!/bin/bash

if [ $APPLICATION_SETTINGS == "development.py" ]; then
        python app.py
else
        gunicorn app:app -b 0.0.0.0:$PORT -w 2
fi