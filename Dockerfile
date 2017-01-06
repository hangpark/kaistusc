FROM ubuntu:16.04
MAINTAINER Hang Park <hangpark@kaist.ac.kr>

# Install packages
RUN apt-get update \
  && apt-get install -y \
    gcc \
    python3.5-dev \
    mysql-client \
    nginx \
    python-virtualenv \
    npm \
    nodejs-legacy \
    git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure Nginx
WORKDIR /etc/nginx/sites-available
ADD conf/kaistusc kaistusc
WORKDIR /etc/nginx/sites-enabled
RUN rm default \
  && ln -s ../sites-available/kaistusc ./kaistusc \
  && echo "\ndaemon off;" >> /etc/nginx/nginx.conf

# Configure uWSGI
RUN mkdir -p /tmp/uwsgi

# Set python virtual environment
RUN mkdir -p /app/kaistusc
WORKDIR /app/kaistusc
ADD requirements.txt requirements.txt
RUN virtualenv --python=python3 venv \
  && /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Add project
ADD ./ ./

# Compile frontend
WORKDIR /app/kaistusc/kaistusc/frontend
RUN npm install \
  && node_modules/bower/bin/bower install --allow-root \
  && node_modules/gulp/bin/gulp.js

# Collect static files
WORKDIR /app/kaistusc
RUN /bin/bash -c "source venv/bin/activate && python kaistusc/manage.py collectstatic --noinput"

# Expose ports
EXPOSE 80 443

# Run server
RUN chmod +x conf/entrypoint.sh
ENTRYPOINT conf/entrypoint.sh
