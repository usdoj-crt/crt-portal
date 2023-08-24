# Pull base image. We use the python image instead of Jupyterhub to be more consistent with available Cloud Foundry buildpacks.
FROM python:3.11.4

# Brings output to the terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Use a shared notebook directory
RUN mkdir -p ./srv/jupyterhub
WORKDIR /srv/jupyterhub
RUN mkdir -p ./assignments

# This must be done as one step to avoid docker caching the update portion:
RUN \
  echo "deb https://deb.nodesource.com/node_14.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  apt-get -y update && \
  apt-get -y install \
    git \
    sudo \
    r-base r-base-dev \
    r-cran-irkernel r-cran-tidyverse r-cran-rpostgresql && \
  apt-get install -yqq nodejs npm && \
  pip install -U pip && \
  pip install pipenv && \
  pip --version && \
  npm i -g npm@^8 && \
  npm -v && \
  node -v i  && \
  rm -rf /var/lib/apt/lists/*

COPY jupyterhub/package*.json /srv/jupyterhub/
RUN npm ci

COPY jupyterhub/Pipfile jupyterhub/Pipfile.lock /srv/jupyterhub
RUN pipenv sync --dev --system

RUN R -e "IRkernel::installspec(user = FALSE)"

COPY jupyterhub/ /srv/jupyterhub/

RUN ln -s "/srv/jupyterhub/node_modules/.bin/configurable-http-proxy" /usr/bin/configurable-http-proxy

# Run as root to allow JupyterHub to spawn containers and create users.
USER root
