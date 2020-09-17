FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY ./src/* /app/
COPY uwsgi.ini /app/
COPY secret/client_secrets.json /app/client_secrets.json
