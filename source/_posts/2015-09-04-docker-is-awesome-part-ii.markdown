---
layout: post
title: "Docker Is Awesome - Part II"
date: 2015-09-04 22:56:15 +0530
comments: true
categories: [devops, docker, aws, nginx]
---

This is Part 2 of the 'Docker Is Awesome' mini-series. You can catch Part 1
over [here]({% post_url 2015-09-03-docker-is-awesome %}).

In this article, I'll explain how to use docker-machine, docker-compose and
docker-engine to deploy your setup on your local machine as well as to AWS.

<!--more-->

It is imperative to first understand what this trinity of tools does. docker-engine is the basic component - it is used to create, manipulate and delete
one-off containers. On the command line, one can invoke it by typing just
`docker`.

docker-compose is a tool built on top of docker-engine which allows us to
run multi-container systems. In our setup, we have three services - django,
postgres and nginx. Each runs in their own container, and compose lets us
coordinate them. The docker-compose reference urges us not to use it in
production *yet*, but it's pretty good, so screw that!

docker-machine is a tool used to create and provision Docker hosts. This
provisioning can be done either on your local machine or on a cloud provider;
it supports quite a few of them, including AWS and DigitalOcean.

Here are the contents of the `rebuild_docker.sh` file -:

``` bash rebuild_docker.sh
docker-compose build
docker-compose up -d
docker-compose ps
```

The `build` option builds each service specified in the `docker-compose.yml` file.
The `up -d` option creates and starts the containers given in that list. Finally,
`ps` lets us see each running container, what command they're running and what
their status is (exit codes if there were any errors).

With all that out of the way, let us begin!

## Local Machine Setup

Let's create a docker-machine host for our local machine. We will be using the Virtualbox
driver to get that running.

``` bash docker-machine local
$ docker-machine create -d virtulabox dev;
Creating VirtualBox VM...
Creating SSH key...
Starting VirtualBox VM...
Starting VM...
To see how to connect Docker to this machine, run: docker-machine env dev
```

Well, since it tells us to -:

``` bash docker-machine local
$ docker-machine env dev
export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://192.168.99.100:2376"
export DOCKER_CERT_PATH="/home/pritishc/.docker/machine/machines/dev"
export DOCKER_MACHINE_NAME="dev"
# Run this command to configure your shell: 
# eval "$(docker-machine env dev)"
```

A bunch of environment variables, hrm. Run the `eval` command as given to set those up.
Now we have a running docker host on our local. Check out the ip of the machine since
you will be needing that later -:

``` bash docker-machine local
$ docker-machine ip dev
192.168.99.100
```

Now we can run the contents of `rebuild_docker.sh` to build, create/start and list our
containers in one go. Note that the building process is initially quite slow; especially
on your local machine. The results of this build will be cached, making each subsequent
build much faster. However, **if you tinker with the Dockerfile of a service (like django),
the lines after the line you tinkered with will not be cached, and will be built again**.

Here's what it looks like when the builds are cached -:

``` bash docker-machine local cached build
postgres uses an image, skipping
Building django...
Step 0 : FROM ubuntu:14.04
 ---> 91e54dfb1179
Step 1 : ENV DJANGO_CONFIGURATION Docker
 ---> Using cache
 ---> 6c23847d177e
Step 2 : RUN apt-get update
 ---> Using cache
 ---> 37ceafd99c8b
Step 3 : RUN apt-get install -y ca-certificates git-core ssh nodejs npm python-pip libpq-dev python-dev
 ---> Using cache
 ---> ca6793a2add5
Step 4 : RUN ln -s /usr/bin/nodejs /usr/bin/node
 ---> Using cache
 ---> f9311c741b62
Step 5 : ENV HOME /root
 ---> Using cache
 ---> b0f6dbd6a6fa
Step 6 : ADD ssh/ /root/.ssh/
 ---> Using cache
 ---> 1a50ee500dba
Step 7 : RUN chmod 600 /root/.ssh/*
 ---> Using cache
 ---> 475bf637fea7
Step 8 : RUN ssh-keyscan bitbucket.org > /root/.ssh/known_hosts
 ---> Using cache
 ---> 1bc79f8a33a0
Step 9 : WORKDIR /usr/src/app
 ---> Using cache
 ---> 6922edc704da
Step 10 : RUN git clone git@bitbucket.org:me/repo.git
 ---> Using cache
 ---> 29160d78c443
Step 11 : WORKDIR /usr/src/app/repo
 ---> Using cache
 ---> ca03b1e414cc
Step 12 : RUN pip install -r requirements.txt
 ---> Using cache
 ---> 56fb3e85c03c
Step 13 : RUN npm install -g bower
 ---> Using cache
 ---> e5660af6e528
Step 14 : RUN bower --allow-root install
 ---> Using cache
 ---> d8b0d8cf33e6
Step 15 : ENV AWS_ACCESS_KEY youcanttouchthis
 ---> Using cache
 ---> 057f430aa52d
Step 16 : ENV AWS_SECRET_ACCESS_KEY secretsauce
 ---> Using cache
 ---> 68291ffdbd6c
Step 17 : ENV S3_BUCKET_NAME datbuckettho
 ---> Using cache
 ---> 2ba6884067d2
Step 18 : ENV DB_NAME postgres
 ---> Using cache
 ---> 951c81446ee1
Step 19 : ENV DB_USER postgres
 ---> Using cache
 ---> b85ead2a75e3
Step 20 : ENV DB_PASS postgres
 ---> Using cache
 ---> 475c43341026
Step 21 : ENV DB_SERVICE postgres
 ---> Using cache
 ---> 4cc910cd2a51
Step 22 : ADD ./static/admin /usr/src/app/repo/static/admin
 ---> Using cache
 ---> d70e3dd5c885
Step 23 : WORKDIR /usr/src/app/repo/project
 ---> Using cache
 ---> 255623db8059
Step 24 : CMD gunicorn project.wsgi -w 2 -b 0.0.0.0:8000 --log-level -
 ---> Using cache
 ---> 55a7c489cb3e
Successfully built 55a7c489cb3e
Building nginx...
Step 0 : FROM nginx
 ---> cd3cf76a61ee
Step 1 : MAINTAINER Pritish Chakraborty
 ---> Using cache
 ---> 73affa8810c3
Step 2 : COPY nginx.conf /etc/nginx/nginx.conf
 ---> Using cache
 ---> 3b73ef0ef3e8
Step 3 : COPY container_ip.sh /root/container_ip.sh
 ---> Using cache
 ---> b3fbe36b0674
Step 4 : RUN /root/container_ip.sh
 ---> Using cache
 ---> 5df4fe6c5403
Step 5 : CMD service nginx restart
 ---> Running in 642215ba03c6
 ---> 4d2df9239cb3
Removing intermediate container 642215ba03c6
Step 6 : CMD /usr/sbin/nginx -g "daemon off;"
 ---> Running in 5bdc232c1761
 ---> 2d55cf5df93b
Removing intermediate container 5bdc232c1761
Successfully built 2d55cf5df93b
projectdocker_postgres_1 is up-to-date
projectdocker_django_1 is up-to-date
Recreating projectdocker_nginx_1...
      Name             Command             State              Ports       
-------------------------------------------------------------------------
projectdocker_dja   gunicorn           Up                 8000/tcp         
ngo_1              project.wsgi -w 2                                       
                   ...                                                    
projectdocker_ngi   /bin/sh -c         Up                 443/tcp, 0.0.0.0 
nx_1               /usr/sbin/nginx                       :80->80/tcp      
                   ...                                                    
projectdocker_pos   /docker-           Up                 5432/tcp         
tgres_1            entrypoint.sh                                          
                   postgres
```

Pretty neat, huh? You can browse to the ip given by docker-machine in your
browser and check your website out in all its glory!

A couple more things - suppose some service breaks unexpectedly. You can
check out the logs using -:

``` bash docker-compose logs
$ docker-compose logs <servicename>
```

If you want to check out the contents of your container, run -:

``` bash docker-compose run
$ docker-compose run <servicename> bash
```

## AWS Setup

This is it. The biggie. This is the part where you get to see your app running
on the cloud. We're going to deploy our multi-container setup to Amazon EC2. But
first, we're going to have to prepare a few things.

* Create a Virtual Private Cloud instance (VPC) which your EC2 instance will use.
This can be done from the VPC Management Console. If you signed up on the free-tier,
you might have a VPC instance running from the beginning. If not, create one!
Here's what it looks like -:

{% img /images/AWS_VPC.png 'AWS VPC' %}

{% img /images/AWS_VPC_Subnets.png 'AWS VPC Subnets' %}

When creating a VPC, keep the tenancy as 'default' and an example of a CIDR block
that you could choose is 172.31.0.0/16, where /16 is the subnet mask. Amazon does
the rest for you.

* With the VPC and its subnets (if there are none, create a public subnet) created,
we need to assign some security groups. First, according to Amazon's [documentation](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Scenario1.html),
make a security group (call it whatever you like) and add the rules as follows -:

{% img /images/AWS_SG_1.png 'AWS Security Group Inbound Rules' %}

{% img /images/AWS_SG_2.png 'AWS Security Group Outbound Rules' %}

In the inbound rules, IP ranges that I pixelized are my own. In these specific rules,
you'd select 'My Own IP' when creating them. Finally, add the security group to your
VPC.

* With the VPC set up, go to the Identity Access Management console (IAM), and
generate a pair of credentials for docker-machine to use when setting up your EC2
box. I wasn't able to figure out the security groups that this set of IAM credentials
should've had, so I gave it FullAdministratorAccess - this is usually not advisable.
Also note that the set of credentials which I put in my django Dockerfile are **not**
the same as these.

Now we can provision our docker host on AWS. Do it with this command -:

``` bash docker-machine AWS
docker-machine create \    
--driver amazonec2 \
--amazonec2-access-key nicekeym8 \
--amazonec2-secret-key oososecret \
--amazonec2-vpc-id vpc-id \
--amazonec2-region some-region \
--amazonec2-zone zone-letter \
ec2box
```

You can get the information from the VPC management console. This command takes a
while to execute, but when it is done, you'll have to run the `eval` command like
we did for our local setup, to point docker-machine to our AWS host.

Once the machine is provisioned, go check it out on your EC2 management console -:

{% img /images/AWS_EC2.png 'AWS EC2' %}

There's still a bit of security group editing to do. Now when you check out your
VPC, you will find that it has a new group called `docker-machine`. Edit this group
and add the following inbound rule -:

{% img /images/AWS_VPC_dockermachine.png 'docker-machine Rules' %}

Add this TCP rule for your own IP.

Now you can browse to the ip given by `docker-machine ip ec2box`/the one listed on
your EC2 instances page, and examine your webapp on the cloud at leisure!
Pat yourself on the back, you did it. Or not...

## What About Nginx?

Ah, so you *did* read my previous article carefully. If I'm right, you'll find
that nginx is giving you weird errors (most likely a 502).

The last bit of trickery that I added to the nginx Dockerfile revolves around this
file - `container_ip.sh`. Its contents are as follows -:

``` bash container_ip.sh
# The awk command gets the IP for the django container from /etc/hosts
# The sed command replaces the placeholder in nginx conf with this IP
# Finally, the config placeholder is replaced with the IP
ip=`awk '/django/ {print $1; exit}' /etc/hosts`; sed -i "s/{{container_ip}}/$ip/g" /etc/nginx/nginx.conf
```

And the said placeholder is put in like this -:

{% raw %}
``` bash nginx config
location / {
    proxy_pass http://{{container_ip}}:8000;
    proxy_set_header   Host $host;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Host $server_name;
}
```

`{{container_ip}}`{% endraw %} is in place of 'django', which is replaced by the actual IP given in
the `/etc/hosts` file of the nginx container - you can confirm this for yourself by running
bash on the nginx container and running the awk and sed commands.

You might want to put `container_ip.sh` in the nginx directory so that docker can
find it when performing the ADD operation.

And now, run the following commands to recreate the nginx container -:

``` bash nginx recreation
$ docker-compose build --no-cache nginx
$ docker-compose up -d
```

And there you have it. Give it a bit of time for AWS to iron everything out, and with
luck, you'll be able to play with your webapp on the cloud.

Hope you enjoyed this article :) I'll write another one soon for that django-storages +
Amazon S3 setup of mine.
