FROM python:3.10.11-slim-buster AS builder

RUN apt-get update -y && apt-get upgrade -y

# COPY requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev


FROM python:3.10.11-slim-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .
CMD ["python", "scheduler.py"]