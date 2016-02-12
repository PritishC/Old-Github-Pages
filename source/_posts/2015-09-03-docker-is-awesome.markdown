---
layout: post
title: "Docker Is Awesome - Part I"
date: 2015-09-03 21:56:16 +0530
comments: true
categories: [devops, docker, aws, django, angular, nginx]
---

It's been a while since I've written a blog post. There's been lots of changes that I've
had to deal with, the big one being a change of workplace. And I realize that this post
should've been the one explaining my adventures with Elasticsearch. That will have to wait
for a bit, my apologies!

In this article, I'm going to explain my (possibly flawed) method of deploying a Django/Angular
app using Docker. I've wanted to learn how to deploy an app to AWS for a while, and Docker
helped me do just that.

<!--more-->

I assume that the reader has a basic knowledge of the docker toolbox; if not, I'll explain them in brief in
part 2. To begin with, here's the directory structure of my app for reference (generated using the
lovely `tree` command on Linux) -:

``` bash app structure
|-- bower.json
|-- CONTRIBUTORS
|-- project
|   |-- project
|   |   |-- aws_settings.py (django-storages credentials here)
|   |   |-- heroku_settings.py
|   |   |-- __init__.py
|   |   |-- settings.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   `-- wsgi.py
|   |-- manage.py
|   |-- app1
|   |   |-- __init__.py
|   |   |-- permissions.py
|   |   |-- serializers.py
|   |   |-- services.py
|   |   |-- tests.py
|   |   `-- views.py
|   `-- users
|       |-- __init__.py
|       |-- models.py
|       |-- permissions.py
|       |-- serializers.py
|       `-- views.py
|-- gulpfile.js
|-- package.json
|-- Procfile
|-- README.md
|-- requirements.txt
|-- scripts
|   `-- postInstall.sh
|-- static
|   |-- javascripts
|   |   |-- app.js
|   |   |-- controllers
|   |   |   `-- controllers.js
|   |   |-- directives
|   |   |   `-- directives.js
|   |   `-- services
|   |       `-- services.js
|   |-- partials (angular view stuff)
|   `-- stylesheets
|       `-- styles.css
|-- templates
|   |-- index.html
|   |-- javascripts.html
|   |-- navbar.html
|   `-- stylesheets.html
```

This follows from the nice boilerplate provided by [thinkster.io](https://github.com/brwr/thinkster-django-angular-boilerplate) - take a look at their nifty tutorials [here](http://thinkster.io).

I first stumbled across this article on [realpython.com](https://realpython.com/blog/python/django-development-with-docker-compose-and-machine/), which greatly piqued my interest. I realized that docker had
moved on to becoming a suite of tools - docker itself becoming docker-engine in name. However,
I faced issues (being a total n00b in devops) in setting up with the configuration that they
specified, so I decided to go for something simpler. I found just what I needed in [Andre's](https://github.com/andrecp/django-tutorial-docker-nginx-postgres)
tutorial for deploying a simple Docker-Nginx-Django-Postgres setup.

One thing I noticed in both configurations is that the code repository was bundled alongwith the docker
stuff (needed by docker-compose) for production.
I couldn't agree with that, so I decided to look up a method to clone my repository while creating
the docker container. I then kept my code and deployment repositories separate, and found that Bitbucket
(where my repositories are hosted) have a feature called deployment keys - SSH keys that have read-only
access to a repository. This was exactly what I needed.

Here is the directory structure of my docker deployment repository -:

``` bash docker directories
|-- docker-compose.yml
|-- Dockerfile
|-- ec2box.sh
|-- nginx
|   |-- container_ip.sh
|   |-- Dockerfile
|   `-- nginx.conf
|-- README.md
|-- rebuild_docker.sh
|-- ssh
|   |-- bb_deploy.rsa
|   |-- bb_deploy.rsa.pub
|   `-- config
`-- static
    `-- admin
```

* docker-compose.yml : The file that controls how docker-compose builds docker containers and runs them
* Dockerfile : The Dockerfile for the django/angular container
* ec2box.sh : A small script containing a single command which creates the whole setup using AWS drivers
* nginx - Directory containing specifics for the nginx container, where container_ip.sh is another
small script which I needed when deploying on AWS
* rebuild_docker.sh : A script from Andre's repository for quickly build-and-up containers using docker-compose
* ssh : Directory containing my Bitbucket deployment key and a SSH config file
* static : Django admin static files

The contents of docker-compose.yml are as follows -:

``` yaml docker-compose.yml
# Nginx
nginx:
    build: ./nginx
    volumes_from:
        - django
    links:
        - django
    ports:
        - "80:80"

# This defines a service for the Django app
# Will include the Angular frontend
django:
    build: .
    volumes:
        - .:/root
        - /usr/src/app
    expose:
        - "8000"
    links:
        - postgres

# This defines a service for the Postgres database
postgres:
    image: postgres:latest
```

Note how the nginx container definition specifies a `volumes_from` section, of which the django
container is a part. The host port 80 has been mapped to container port 80, as nginx requires.
One little caveat: make sure that no other docker containers are hogging up port 80, because you
will have a painful time trying to find out why your nginx container keeps dying on you. The `links`
directive creates entries in the nginx container's `/etc/hosts` file for the django container's IP/hostname.
This will come in use later when we deploy to AWS.

The django container definition has a few small differences from the one mentioned at realpython or
Andre's tutorial. We mount the volume on `/root` instead of `/usr/src/app`, because the latter does
not exist until we clone the code repository. Additionally, we expose `/usr/src/app` as a volume, so
that the nginx container does not run into a load of 404s when trying to serve static files. Port 8000
is exposed as we shall be running gunicorn on that port, and there is a link to the postgres container.

The postgres definition is not much to talk about, as it is built from an image from the docker registry
(yes, they have a registry of known docker containers!).


Let's take a look at the Dockerfile for the django container -:

``` sh Dockerfile (django)
FROM ubuntu:14.04

ENV DJANGO_CONFIGURATION Docker

# First, we need to get git, and clone our repository
# Additionally, get everything else here too, such as nodejs and npm

RUN apt-get update
RUN apt-get install -y ca-certificates git-core ssh nodejs npm python-pip libpq-dev python-dev
RUN ln -s /usr/bin/nodejs /usr/bin/node

ENV HOME /root

# Add custom ssh keypair - usually Bitbucket deployment keys
ADD ssh/ /root/.ssh/

# Fix permissions
RUN chmod 600 /root/.ssh/*

# Avoid first connection host confirmation
RUN ssh-keyscan bitbucket.org > /root/.ssh/known_hosts

# Clone the repo
WORKDIR /usr/src/app
RUN git clone git@bitbucket.org:username/repo

# Install requirements
WORKDIR /usr/src/app/repo
RUN pip install -r requirements.txt
RUN npm install -g bower
RUN bower --allow-root install

# S3 Storage for django-storages
ENV AWS_ACCESS_KEY yourkeyhere
ENV AWS_SECRET_ACCESS_KEY yoursecretsaucehere
ENV S3_BUCKET_NAME yourbucketnamehere

# DB Settings
ENV DB_NAME postgres
ENV DB_USER postgres
ENV DB_PASS postgres
ENV DB_SERVICE postgres

# Add Django Admin CSS
ADD ./static/admin /usr/src/app/repo/static/admin

WORKDIR /usr/src/app/repo/defsec
CMD ["gunicorn", "app.wsgi", "-w", "2", "-b", "0.0.0.0:8000", "--log-level", "-"]
```

The `DJANGO_CONFIGURATION` environment variable is used in django project settings. First, we
install all the necessary command line tools, and create a symbolic link so that nodejs plays
well. We then add our custom keypair to the `.ssh` directory, and run a permissions fix command.
This will allow us to clone the code repository. Before running the clone command, we run a
`ssh-keyscan` so that the cloning process is automatic - no key passphrase prompts. Some may argue
that this lowers security, but that is a topic for another post altogether.
After cloning, I install all django/angular requirements using pip and bower. A few more environment
variables are then set, first for django-storages (a topic for a soon-to-come post: how I set up
image uploads to Amazon S3 with django-storages) and then for the postgres database. Finally,
django admin static files are added (yes, these don't come out of nowhere, they need to be added
for nginx to serve them) and run the gunicorn server.

With that covered, let's check out the contents of the nginx directory. First up is the nginx
Dockerfile -:

``` sh nginx Dockerfile
# Set nginx base image
FROM nginx

# File Author / Maintainer
MAINTAINER Pritish Chakraborty

# Copy custom configuration file from the current directory
COPY nginx.conf /etc/nginx/nginx.conf

# Uncomment the commented Dockerfile lines below when pushing to AWS
# COPY container_ip.sh /root/container_ip.sh

# Get django container's IP and put it in nginx.conf
# RUN /root/container_ip.sh

# Reload the damn nginx service
# CMD ["service", "nginx", "restart"]
CMD /usr/sbin/nginx -g "daemon off;"
```

Not much to explain here until I get to the part about deploying to AWS. Here's nginx.conf -:

``` sh nginx.conf
worker_processes 1;

events {
    worker_connections 1024;
}

http {

    server {
        listen 80;
        server_name example.org;

        access_log /dev/stdout;
        error_log /dev/stdout info;

        location /static/ {
            alias /usr/src/app/repo/static;
        }

        location /static/javascripts/ {
          default_type text/javascript;
          alias /usr/src/app/repo/static/javascripts/;
        }

        location /static/stylesheets/ {
          default_type text/css;
          alias /usr/src/app/repo/static/stylesheets/;
        }

	location /static/bower_components/ {
	  types {
	    text/css css;
	    text/javascript js;
	  }
	  alias /usr/src/app/repo/static/bower_components/;
	}

	location /static/partials/ {
	  types {
	    text/html html;
	  }
	  alias /usr/src/app/repo/static/partials/;
	}

	location /static/admin/ {
          alias /usr/src/app/repo/static/admin/;
	}

	location /static/admin/css {
	  default_type text/css;
	  alias /usr/src/app/repo/static/admin/css;
	}

	location /static/admin/js {
	  default_type text/javascript;
	  alias /usr/src/app/repo/static/admin/js;
	}

	location /static/admin/img {
	  types {
	    image/png png;
	    image/jpeg jpg;
	  }
	  alias /usr/src/app/repo/static/admin/img;
	}

        location / {
            proxy_pass http://django:8000;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    }
}
```

As you can see, I had to make it very thorough about what files nginx was going to serve,
from where, and what type mappings would the files have had. The latter had me stumped for
a bit - I got nginx to serve all static files, but it was as if the browser didn't know
what to do with them, so take note. Finally, the location directive tells nginx whom
to proxy pass (django container service). There will be a minor change to this bit later
when we deploy on AWS.

The second part of this post will deal with the actual commands needed to deploy the setup;
first, on my local machine (virtualbox driver), and then on AWS. I'll add a bonus command
to deploy to DigitalOcean for shits and giggles.
Coming soon!
