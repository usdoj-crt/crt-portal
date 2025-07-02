# Pull base image. We use the python image instead of Jupyterhub to be more consistent with available Cloud Foundry buildpacks.
FROM python:3.13.3

# Brings output to the terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Use a shared notebook directory
RUN mkdir -p ./srv/jupyterhub
WORKDIR /srv/jupyterhub
RUN mkdir -p ./assignments

# This must be done as one step to avoid docker caching the update portion:
RUN \
  echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
  curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
  apt-get -y update && \
  apt-get -y install \
    git \
    sudo \
    r-base r-base-dev \
    r-cran-irkernel r-cran-tidyverse r-cran-rpostgresql && \
  apt-get install -yqq nodejs && \
  pip install -U pip && \
  pip install pipenv && \
  pip --version && \
  node -v i  && \
  rm -rf /var/lib/apt/lists/*

# TODO: Install this from package-lock.json
RUN npm install -g configurable-http-proxy@^4.5.6

COPY jupyterhub/Pipfile jupyterhub/Pipfile.lock /srv/jupyterhub
RUN pipenv sync --dev --system

RUN R -e "IRkernel::installspec(user = FALSE)"

COPY jupyterhub/ /srv/jupyterhub/

# Run as root to allow JupyterHub to spawn containers and create users.
USER root
