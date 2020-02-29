FROM sanicframework/sanic:LTS

RUN mkdir -p /srv
COPY feedback_validation/ /srv

RUN python3 -m pip install -r /srv/requirements.txt

EXPOSE 8888
WORKDIR /srv
ENTRYPOINT ["python3", "/srv/server.py"]
