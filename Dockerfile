FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8

RUN apk add --no-cache nginx alpine-sdk
RUN python3 -m pip install --upgrade pip

# Copy operations
COPY ./nginx.tmpl /etc/nginx/nginx.tmpl
COPY ./feedback_validation /app
COPY ./prestart.sh /app/prestart.sh

# Configuration
RUN python3 -m pip install -r /app/requirements.txt
