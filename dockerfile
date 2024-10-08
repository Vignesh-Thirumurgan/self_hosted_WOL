FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    pkg-config \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip

RUN pip install -r requirements.txt



COPY . .

EXPOSE 5000

CMD [ "python3", "app.py" ]

