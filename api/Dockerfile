FROM python:alpine

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["/bin/sh", "-c", "python main.py"]