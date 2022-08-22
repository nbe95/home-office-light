FROM python:3.7-slim-bullseye

LABEL author="Niklas Bettgen, niklas@bettgen.de"
WORKDIR /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /app/src/
COPY static/ /app/static/
COPY templates/ /app/templates/

COPY requirements.txt /app/
RUN pip install --upgrade -r requirements.txt

EXPOSE 9000
EXPOSE 9080

ENTRYPOINT ["python"]
CMD ["/app/src/main.py"]
