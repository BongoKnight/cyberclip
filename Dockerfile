FROM python:3.12-alpine

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY src/ /app
WORKDIR /app
CMD ["python", "/app/cyberclip/server.py"]
EXPOSE 8000