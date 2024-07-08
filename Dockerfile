FROM python:3.10.12-slim
LABEL org.opencontainers.image.source https://github.com/valentim/cgen
LABEL org.opencontainers.image.licenses MIT

RUN useradd --user-group --system --create-home --no-log-init cgen
RUN export PATH="/home/cgen/.local/bin:$PATH"

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=on
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

USER cgen
WORKDIR /app

COPY . /app/

USER root
RUN pip install -U pip poetry

RUN  poetry install --only main

USER cgen

COPY /datasets /app/datasets

USER root

RUN chmod +x /app/run.sh

WORKDIR /app

CMD [ "/app/run.sh" ]
