FROM ubuntu:latest
MAINTAINER Mike Wilson <geekinutah@gmail.com>

ENV TERM=xterm-256color

COPY fix-requirements.py /usr/bin/fix-requirements.py
COPY openrc.j2 /openrc.j2

RUN apt-get -q update >/dev/null \
  && apt-get install -y python python-dev curl build-essential git libssl-dev libmysqlclient-dev apache2 libapache2-mod-wsgi\
  && git clone --branch stable/ocata https://github.com/openstack/keystone.git \
  && curl https://bootstrap.pypa.io/get-pip.py | python \
  #&& fix-requirements.py --map_file libs.vers --requirements_file keystone/requirements.txt --inplace \
  #&& pip install keystonemiddleware==4.4.1 \
  && pip install keystone/ \
  && pip install mysqlclient \
  && pip install PyMySQL \
  && pip install Jinja \
  && mkdir /etc/keystone \
  # Cleanup
  && apt-get clean autoclean \
  && apt-get autoremove --yes \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ 

COPY keystone.conf.j2 /etc/keystone/keystone.conf.j2
COPY keystone-paste.ini /etc/keystone/keystone-paste.ini
COPY apache2-keystone.conf.j2 /etc/apache2/sites-available/keystone.conf
COPY start_keystone.sh /usr/bin/start_keystone.sh

ENTRYPOINT ["/usr/bin/start_keystone.sh"]
