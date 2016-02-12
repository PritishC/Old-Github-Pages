---
layout: post
title: "Beginning Tryton"
date: 2014-10-21 12:05:18 +0530
comments: true
categories: tryton
---

Before we go through the setup of the Tryton client and server, one should go
through setting up the [virtualenv]({% post_url 2014-10-16-virtualenv-setup-for-tryton %})
and [postgres]({% post_url 2014-10-19-postgres-setup %}).
Also, install `libxslt-dev` (and perhaps `libz-dev` as well) with your package 
manager because the `lxml` package needs it.

<!--more-->

Right, now let's activate our virtualenv and install the requisite packages.

``` bash installing tryton/trytond
$ workon trytonenv
$ pip install trytond trytond-party trytond-company trytond-country trytond-currency
$ pip install tryton
$ pip install psycopg2 # Required for DB connectivity.
```

The packages that follow `trytond` are Tryton modules. `trytond` is the server
and `tryton` is the client. Any server needs a configuration file, and we have
one for ours too. Picked up from the Gentoo wiki -:

{% include_code sample trytond.conf lang:text trytond.conf %}

You might want to change the value of the `db_password` field there, to the pass
that you had set for the postgres role earlier. You will be using this pass to
login to a database in Tryton.

Now, fire up two terminal windows or tabs, and run the following commands separately
in each -:

``` bash tryton start
$ trytond -c path/to/trytond.conf
$ tryton -dv
```

The `-dv` switch will allow you to see errors and other messages on the command
line for the Tryton client in a verbose manner.

You will arrive at a screen to login to the demo profile. Close that, and head
to File->Database->New Database. Note that the default administrator password
for Tryton is `admin`. Here, the `admin_passwd` field has been inserted to change
the default. One could remove this field if they wished.

<img src="{{ root_url }}/images/tryton-createdb.png" />

Congratulations, you've created your very first Tryton database. Now you can login
to it and install the necessary Tryton modules.
