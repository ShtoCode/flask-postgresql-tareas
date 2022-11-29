FROM alpine:3.16

RUN apk add --no-cache python3-dev \
    && python-pip3