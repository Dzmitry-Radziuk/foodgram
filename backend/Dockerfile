FROM python:3.11-alpine

ENV DJANGO_SETTINGS_MODULE=backend.settings
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    build-base \
    graphviz \
    graphviz-dev \
    libffi-dev \
    musl-dev \
    gcc \
    py3-pip \
    jpeg-dev \
    zlib-dev \
    python3-dev \
    py3-setuptools \
    netcat-openbsd 

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

CMD ["sh", "entrypoint.sh"]