#!/bin/sh

#cd ~/PycharmProjects/ome2.0

pytest
if [ $? -ne 0 ]; then
    echo "Tests failed. Exiting..."
    exit 1
else
    echo "All tests passed!"
fi

pip freeze > requirements.txt
sam sync --stack-name=ome-restaurant-app
