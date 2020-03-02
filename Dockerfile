FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8
RUN mkdir /run/nginx/
RUN apk add --no-cache nginx alpine-sdk gettext
RUN python3 -m pip install --upgrade pip

# Install app
COPY ./feedback_validation /app
RUN python3 -m pip install -r /app/requirements.txt

# Nginx stuff
COPY ./nginx.tmpl /app/nginx.tmpl
COPY ./prestart.sh /app/prestart.sh


ENV PORT=4000

EXPOSE 80
