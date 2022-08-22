FROM python:3.7-slim-bullseye

LABEL author="Niklas Bettgen, niklas@bettgen.de"
WORKDIR /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /app/
COPY templates/ /app/
COPY static/ /app/

COPY requirements.txt /app/
RUN pip install --upgrade -r requirements.txt

EXPOSE 9000
EXPOSE 9080

ENTRYPOINT ["python"]
CMD ["/app/src/main.py"]
