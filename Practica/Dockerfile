FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install .

USER app

EXPOSE 8080

CMD ["python", "-m", "sog2.server"]

