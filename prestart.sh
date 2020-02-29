#!/bin/sh
envsubst '$${FEEDBACK_DOMAINS}' < /app/nginx.tmpl > /etc/nginx/nginx.conf && nginx || cat /etc/nginx/nginx.conf
