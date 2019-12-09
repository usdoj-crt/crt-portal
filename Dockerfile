# Pull base image
FROM python:3.7

# Set environment varibles,
ENV PYTHONDONTWRITEBYTECODE 1
# brings output to the terminal
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# get binary dependencies
RUN \
  apt-get update && \
  apt-get install -y apt-utils && \
  apt-get install -y libxmlsec1 libxmlsec1-openssl xmlsec1 && \
  apt-get install -y apt-transport-https

# Install Python dependencies
RUN pip install pipenv

COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system

# Install Node and npm dependencies
RUN \
  echo "deb https://deb.nodesource.com/node_10.x stretch main" > /etc/apt/sources.list.d/nodesource.list && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
  wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
  apt-get update && \
  apt-get install -yqq nodejs yarn && \
  pip install -U pip && pip install pipenv && \
  npm i -g npm@^6 && \
  rm -rf /var/lib/apt/lists/*

RUN npm install --system

# Copy project
COPY . /code/