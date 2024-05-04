if sudo docker ps -a --format '{{.Names}}' | grep -q '^namaste_bali_panel_api$'; then
    sudo docker stop namaste_bali_panel_api && sudo docker rm namaste_bali_panel_api &&
    sudo docker build -t namaste_bali_panel_api . &&
    sudo docker run -v ./uploads:/uploads --name namaste_bali_panel_api --env-file .env -p 8282:8080 -d namaste_bali_panel_api
else
       sudo docker build -t namaste_bali_panel_api . &&
           sudo docker run -v ./uploads:/uploads --name namaste_bali_panel_api --env-file .env -p 8282:8080 -d namaste_bali_panel_api
fi
