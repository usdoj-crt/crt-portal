# Pull base image
FROM python:3.12.2

# Set environment varibles,
ENV PYTHONDONTWRITEBYTECODE 1
# brings output to the terminal
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install Python dependencies
RUN \
  pip install --upgrade pip && \
  pip install pipenv

COPY Pipfile Pipfile.lock /code/
RUN pipenv sync --dev --system

RUN \
  apt-get update && \
  apt-get install -yqq apt-transport-https && \
  apt-get autoremove -y

RUN \
  echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
  curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
  apt-get update && \
  apt-get install -yqq nodejs && \
  node -v i && \
  rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json /code/
RUN npm install

# Install gettext for i18n
RUN apt-get update && apt-get install -y gettext

# Copy project
COPY . /code/
