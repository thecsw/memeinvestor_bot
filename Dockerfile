FROM python:alpine

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src .

CMD ["python", "main.py"]
