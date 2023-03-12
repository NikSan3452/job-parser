###########
# BUILDER #
###########

FROM python:3.11.1-slim-bullseye as builder

WORKDIR /job_parser

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt -y install netcat gcc postgresql python3-dev musl-dev \
    && apt clean
RUN apt update

RUN pip install --upgrade pip
RUN pip install flake8
COPY . .
RUN flake8 --ignore=E501,F401 ./job_parser

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /job_parser/wheels -r requirements.txt


#########
# FINAL #
#########
FROM python:3.11.1-slim-bullseye

RUN mkdir -p /home/job_parser
RUN addgroup --system job_parser && adduser --system job_parser --gecos job_parser

ENV HOME=/home/job_parser
ENV JOB_PARSER_HOME=/home/job_parser/django
RUN mkdir $JOB_PARSER_HOME
RUN mkdir $JOB_PARSER_HOME/staticfiles
RUN mkdir $JOB_PARSER_HOME/mediafiles
WORKDIR $JOB_PARSER_HOME

RUN apt-get update && apt-get install -y libpq-dev
RUN apt-get update && apt-get install -y netcat
COPY --from=builder /job_parser/wheels /wheels
COPY --from=builder /job_parser/requirements.txt .
RUN pip install --no-cache /wheels/*
RUN playwright install
RUN playwright install-deps

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $JOB_PARSER_HOME/entrypoint.sh

COPY . $JOB_PARSER_HOME

USER root

RUN chmod +x  $JOB_PARSER_HOME/entrypoint.sh
RUN chown -R job_parser:job_parser $JOB_PARSER_HOME

USER job_parser

ENTRYPOINT ["/home/job_parser/django/entrypoint.sh"]

