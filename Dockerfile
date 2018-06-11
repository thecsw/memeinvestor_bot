FROM python:alpine

RUN apk add --update --no-cache g++

RUN adduser -D user
USER user
WORKDIR /home/user
COPY --chown="user:user" requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown="user:user" src/ .

CMD ["python", "main.py"]
