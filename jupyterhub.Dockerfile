FROM jupyterhub/jupyterhub:3.1.1

WORKDIR /srv/jupyterhub

RUN apt-get -y update
RUN apt-get -y install sudo r-base r-base-dev

RUN useradd -m dev
RUN echo 'dev:password' | chpasswd

# Use a shared notebook directory
RUN mkdir -p ./assignments

# Make a jupyter user, and let it spawn notebooks as root:
RUN useradd --no-create-home -b /srv/jupyterhub jupyter
RUN adduser jupyter sudo
RUN chown -R jupyter .
RUN echo 'root ALL=(ALL:ALL) ALL' > /etc/sudoers
RUN echo 'jupyter ALL=(ALL) NOPASSWD: /usr/local/bin/sudospawner' >> /etc/sudoers

RUN apt-get -y install r-cran-irkernel r-cran-tidyverse r-cran-rpostgresql
RUN pip install --upgrade pip
RUN pip install pipenv
COPY jupyterhub/Pipfile jupyterhub/Pipfile.lock /srv/jupyterhub
RUN pipenv install --dev --system
RUN R -e "IRkernel::installspec(user = FALSE)"

USER jupyter
