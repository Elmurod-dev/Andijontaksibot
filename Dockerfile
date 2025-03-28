FROM python:3.12
WORKDIR /app
COPY . .
RUN apt update && apt install -y curl make && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
RUN make --version
CMD ["sh", "-c", "alembic downgrade base && make mig && python3 main.py"]
