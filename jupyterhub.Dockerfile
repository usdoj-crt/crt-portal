FROM jupyterhub/jupyterhub:3.1.1
ARG dev_password

WORKDIR /srv/jupyterhub

RUN apt-get -y update
RUN apt-get -y install sudo r-base r-base-dev

RUN useradd -m dev --shell /bin/bash
RUN echo dev:${dev_password} | chpasswd

# Use a shared notebook directory
RUN mkdir -p ./assignments

# Make a jupyter user, and let it spawn notebooks as root:
RUN useradd --no-create-home -b /srv/jupyterhub jupyter
RUN adduser jupyter sudo
RUN chown -R jupyter .
RUN echo 'root ALL=(ALL:ALL) ALL' > /etc/sudoers
RUN echo 'jupyter ALL=(ALL) NOPASSWD: /usr/local/bin/sudospawner' >> /etc/sudoers
RUN usermod -aG shadow jupyter

RUN apt-get -y install r-cran-irkernel r-cran-tidyverse r-cran-rpostgresql
RUN pip install --upgrade pip
RUN pip install pipenv
COPY jupyterhub/Pipfile jupyterhub/Pipfile.lock /srv/jupyterhub
RUN pipenv sync --dev --system
RUN R -e "IRkernel::installspec(user = FALSE)"

COPY jupyterhub/export_embed.py /srv/jupyterhub/export_embed.py

USER jupyter
