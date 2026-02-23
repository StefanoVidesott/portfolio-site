FROM python:3.10-slim

WORKDIR /portfolio

COPY ./requirements.txt /portfolio/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /portfolio/requirements.txt

COPY ./app /portfolio/app
COPY ./seed.py /portfolio/seed.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
