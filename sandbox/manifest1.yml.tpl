---
applications:
- name: crt-portal-sandbox-worker1-WHOAMI
  memory: 256M
  instances: 1
  buildpacks:
  - https://github.com/cloudfoundry/apt-buildpack
  - python_buildpack
