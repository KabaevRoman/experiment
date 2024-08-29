FROM python:3.11.9-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update && \
    apk add --virtual build-deps gcc musl-dev && \
    apk add postgresql-dev && \
    apk add netcat-openbsd &&  \
    apk add libffi-dev && \
    apk add build-base python3-dev


RUN mkdir src
COPY ./requirements.txt src/
RUN pip install -r src/requirements.txt
COPY . src/
WORKDIR src