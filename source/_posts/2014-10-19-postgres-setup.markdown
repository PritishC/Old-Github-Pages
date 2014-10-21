---
layout: post
title: "Postgres Setup"
date: 2014-10-19 20:27:55 +0530
comments: true
categories: [tryton, postgresql] 
---

This article offers a simple introduction to PostgreSQL and how to install it.
It is necessary for Tryton. In effect, this article is merely filler, and one can
skip it if one wishes so.

[PostgreSQL](http://www.postgresql.org/) is an open-source ORDBMS which is a hardcore
programmer's paradise. Since it is community-developed, it adheres to strict standards
and supports DB best practices. For more information, Google is your friend.

Now the installation of Postgres on your setup depends on the operating system you
have installed. For most Linux distros, Postgres has a distro-specific bundle which
can easily be installed using the particular package manager. It is usually advised 
to install this distro-specific bundle rather then going down the generic route.

I had faced several problems setting up Postgres on Linux Mint because I downloaded
and executed the generic bundle. You can find some mention of those problems here 
at the [wiki](https://github.com/PritishC/nereid-erms/wiki) of a project which I 
wrote as part of a company induction task. I am currently on Lubuntu, and this 
time, I used the package manager. Lesson learned.

Another thing you ideally should do is install [PGAdmin](http://www.pgadmin.org/). 
It is a very useful tool for management and administration of your databases. You
might often have to view a specific table inside the DB that you create for Tryton.

For Debian derivatives such as mine, 

``` bash bash snippet
$ sudo apt-get install postgresql postgresql-contrib
$ sudo apt-get install pgadmin3
```

There is also the `postgres` user setup. After one is done installing the above,
one should fire up a terminal and set the `postgres` user's password.

``` bash postgres user
$ sudo -u postgres psql postgres
$ \password postgres
```

Equivalently, one could do `sudo su - postgres` to get into the postgres account,
and then run `psql -u postgres -h localhost` or something similar.
The second line in the above snippet sets a password for the postgres database 
role.

And that's that. Soon, we shall be on a functioning Tryton setup!

