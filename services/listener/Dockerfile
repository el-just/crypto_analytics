FROM python:3.8.0-alpine3.10

WORKDIR /usr/src/app
RUN apk add --no-cache gcc musl-dev linux-headers
COPY ./services/listener ./service
COPY ./ca_common ./ca_common
WORKDIR /usr/src/app/service
RUN \
    apk add make && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

CMD [ "python", "-u", "run.py" ]
