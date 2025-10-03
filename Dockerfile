FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./app/requirements ./requirements

RUN pip install --no-cache-dir  -r requirements/dev.txt

COPY ./app .


EXPOSE 8000

# CMD ["alembic upgrade head", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["./script.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8003 --reload"]