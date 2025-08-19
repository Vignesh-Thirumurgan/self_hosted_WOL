# Wake-on-lan
This is the simple flask to app to turn on the system within the network using wake on lan.


## Run it on docker. Below is the docker-compose file.

```yaml
services:
  web:
    image: craze477/wakeonlan
    network_mode: "host"
    container_name: wakeonlan
    environment:
      DB_HOST: 127.0.0.1 
      DB_USER: WAKE
      DB_PASSWORD: WAKE
      DB_NAME: WAKE
    depends_on:
      - db
    command: sh -c "sleep 50 && python app.py"
    

  db:
    image: mysql:8.0
    network_mode: "host"
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: WAKE
      MYSQL_USER: WAKE
      MYSQL_PASSWORD: WAKE
      MYSQL_DATABASE: WAKE
    volumes:
      - /path/to:/var/lib/mysql
