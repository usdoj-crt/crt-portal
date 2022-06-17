# Pull base image
FROM python:3.9.12

# Set environment varibles,
ENV PYTHONDONTWRITEBYTECODE 1
# brings output to the terminal
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile Pipfile.lock /code/
RUN pipenv install --dev --system

# Install Node and npm dependencies
RUN \
  apt-get update && \
  apt-get install -yqq apt-transport-https
RUN \
  echo "deb https://deb.nodesource.com/node_14.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  apt-get update && \
  apt-get install -yqq nodejs && \
  pip install -U pip && pip install pipenv && \
  npm i -g npm@^8 && \
  pip --version && \
  npm -v && \
  node -v i  && \
  rm -rf /var/lib/apt/lists/*

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied

COPY package*.json /code/

RUN npm install

# Install gettext for i18n
RUN apt-get update && apt-get install -y gettext

# Copy project
COPY . /code/
