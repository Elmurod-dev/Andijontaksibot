FROM python:3.12
WORKDIR /app
COPY . .
RUN apt update && apt install -y curl make && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
RUN make --version
CMD ["sh", "-c", "make mig && python3 main.py"]
