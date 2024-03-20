docker build -t chat_app . && docker run &&
docker run --name chat_app --env-file .env -p 8181:8000 -d chat_app
