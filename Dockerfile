FROM tiangolo/uvicorn-gunicorn:latest

COPY ./feedback_validation /app
RUN python3 -m pip install -r /app/requirements.txt
