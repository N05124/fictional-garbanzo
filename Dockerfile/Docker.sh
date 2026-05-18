#==================Docker.sh==================
#!/bin/bash

cd ~/Documents/Jupyter || exit

docker compose build
docker compose up -d

sleep 3

open "http://localhost:8888/lab"
