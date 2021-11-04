docker run -d \
  --name task \
  --mount type=volume, src=task-static, dst=static/data \
  task:0.1

docker volume create \
--driver local \
-o o=bind \
-o type=none \
-o device="/root/nms" \
nmsvol