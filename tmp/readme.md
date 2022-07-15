docker build -t web-server-fastapi -f web-server\.docker\dockerfile .\ --no-cache

docker run --rm -it --entrypoint bash web-server-fastapi
docker run --rm -it -p 8000:8000 --name web-server web-server-fastapi

docker tag web-server-fastapi cr.yandex/crp9627nqo84cq3jgv7v/web-server-fastapi

docker push cr.yandex/crp9627nqo84cq3jgv7v/web-server-fastapi

docker run --rm -it -p 8000:8000 --name web-server cr.yandex/crp9627nqo84cq3jgv7v/web-server-fastapi

docker run --rm -it -p 8080:8080 --name web-server web-server-fastapi --host 0.0.0.0 --port 8080

