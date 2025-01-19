FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Installing Rust because of the Tantivy dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  libffi-dev \
  libssl-dev \
  sqlite3 \
  libsqlite3-dev \
  && curl https://sh.rustup.rs -sSf | sh -s -- -y \
  && export PATH="/root/.cargo/bin:$PATH" \
  && rustc --version \
  && cargo --version \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN mkdir -p /data
CMD ["gunicorn", "-c", "gunicorn.conf.py", "manage:app"]