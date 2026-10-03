FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
COPY requirements.txt .
RUN pip install --no-cache-dir pandas numpy duckdb pyspark pytest
COPY . .
CMD ["sh", "-c", "python -m src.generate_data && python -m src.local_pipeline && python -m src.spark_pipeline"]
