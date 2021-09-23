FROM python:3.9-alpine

WORKDIR /app

COPY src/ .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
