# pull official base image
FROM python:3.8

# set work directory
WORKDIR /usr/src/cod

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip && pip install pipenv
COPY backend/Pipfile .
RUN pipenv install

# copy project
COPY . .