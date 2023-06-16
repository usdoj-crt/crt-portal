FROM jupyterhub/jupyterhub:3.1.1
WORKDIR /srv/jupyterhub

# Use a shared notebook directory
RUN mkdir -p ./assignments

# This must be done as one step to avoid docker caching the update portion:
RUN \
  apt-get -y update && \
  apt-get -y install \
    sudo \
    r-base r-base-dev \
    r-cran-irkernel r-cran-tidyverse r-cran-rpostgresql

RUN pip install --upgrade pip
RUN pip install pipenv
COPY jupyterhub/Pipfile jupyterhub/Pipfile.lock /srv/jupyterhub
RUN pipenv sync --dev --system
RUN R -e "IRkernel::installspec(user = FALSE)"

COPY jupyterhub/ /srv/jupyterhub/

# Run as root to allow JupyterHub to spawn containers and create users.
USER root
