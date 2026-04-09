FROM python:3.14-slim

WORKDIR /portfolio

COPY ./requirements.txt /portfolio/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /portfolio/requirements.txt

COPY ./tools /portfolio/tools
COPY ./app /portfolio/app

# Minify JS and CSS assets at build time
RUN python tools/minify.py

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser

# Transfer ownership so the application can read its own files, then lock
# the directory against writes (the app never needs to write to /portfolio/app).
RUN chown -R appuser:appgroup /portfolio && \
    chmod -R 550 /portfolio/app

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
