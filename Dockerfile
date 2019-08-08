# Pull base image
FROM python:3.7

# Set environment varibles,
ENV PYTHONDONTWRITEBYTECODE 1
# brings output to the terminal
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system

# Copy project
COPY . /code/