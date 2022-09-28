# Веб-сервис, выгружающий космические снимки и определяющий NDVI на поле, предоставляя REST API.

## Сервис располагается на собственном VDS-сервере, реализован на FastAPI с использованием PostgreSQL, uvicorn, gunicorn, nginx.

*P.S. Иногда возможны перебои в работе сервера, из-за загрузки других проектов и предоставления им онлайн-жизни.*

*UPDATE: Сервер временно выключен и недоступен*

### Функционал:

1. Можно добавить и удалить сельхоз поле в формате GeoJSON.
2. Получить снимок поля по API поставщиков космических снимвков (sentinelsat)
3. Получить изображение поля с NDVI.

### Описание работы веб-сервиса:

* http://95.217.64.252:80/add

Принимает POST запрос в формате [GeoJSON](https://ru.wikipedia.org/w/index.php?title=GeoJSON&stable=1). Обязательно наличие поля `name`.

Пример:

```
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              55.88951110839843,
              53.349321688468414
            ],
            [
              56.064605712890625,
              53.349321688468414
            ],
            [
              56.064605712890625,
              53.452487004641746
            ],
            [
              55.88951110839843,
              53.452487004641746
            ],
            [
              55.88951110839843,
              53.349321688468414
            ]
          ]
        ]
      }
    }
  ],
  "name": "EXAMPLE"
}
```

В случае успешного запроса сервер ответит:

```
Success! For NDVI and SNAPSHOT, use the name = EXAMPLE.
```

* http://95.217.64.252:80/show/

Принимает GET запрос с параметром `name`.

В случае успешного запроса отправляет изображение в формате `.tiff`. (Изображение весит в среднем более 400 МБ)

* http://95.217.64.252:80/ndvi/

Принимает GET запрос с параметром `name`.

В случае успешного запроса отправляет изображение в формате `.tiff`. (Изображение весит в среднем более 400 МБ)

* http://95.217.64.252:80/delete/

Принимает GET запрос с параметром `name`.

Удаляет всё прилагающееся к данному ключу (запись из бд, файлы). В случае успешного запроса сервер ответит:

```
Success!
```

### Коллекция [POSTMAN](https://github.com/192117/task_from_agro/blob/master/AGRO.postman_collection.json)

### Настройки NGINX

```
[Unit]
Description=Gunicorn Daemon for FastAPI AGRO Application
After=network.target

[Service]
User=kokoc
Group=www-data
WorkingDirectory=/home/kokoc/task_from_agro
ExecStart=/home/kokoc/task_from_agro/venv/bin/gunicorn app:app -k uvicorn.workers.UvicornWorker \
	  --timeout 800 \
	  --log-level 'debug' \
	  --access-logfile /home/kokoc/task_from_agro/access_log \
	  --error-logfile /home/kokoc/task_from_agro/error_log

[Install]
WantedBy=multi-user.target

```

```
server {
    listen __;
    server_name ip {server_name};

    location / {
        proxy_pass ____;
	proxy_read_timeout 600;
	proxy_send_timeout 600;
	proxy_connect_timeout 600;
    }
    proxy_buffers 8 8k;
    proxy_buffer_size 8k;
    proxy_read_timeout 120s;
}

```
