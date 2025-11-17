FROM python:3.12-alpine

WORKDIR /model-service

COPY . .

CMD ["echo", "success"]