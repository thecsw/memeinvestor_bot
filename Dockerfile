FROM python:alpine

RUN apk add --update --no-cache mariadb-dev g++ gettext
RUN adduser -D user
USER user
WORKDIR /home/user
COPY --chown="user:user" requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY --chown="user:user" src/ .

COPY --chown="user:user" docker/config.py /
COPY --chown="user:user" docker/entrypoint.sh .
RUN chmod +x ./entrypoint.sh

ENV BOT_DRY_RUN=True MYSQL_PORT=3306

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "main.py"]
