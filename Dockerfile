FROM python:3.11-slim-bullseye

# ENV Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app


COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    poppler-utils \ 
    libmagic1 \
    build-essential \
    && apt-get clean

RUN python3 -m pip  --no-cache-dir install -r requirements.txt

COPY . .
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh


EXPOSE 8000
ENTRYPOINT [ "./docker-entrypoint.sh" ]