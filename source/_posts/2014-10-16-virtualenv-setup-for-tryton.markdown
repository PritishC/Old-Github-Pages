---
layout: post
title: "Virtualenv Setup for Tryton"
date: 2014-10-16 22:31:26 +0530
comments: true
categories: [tryton, virtualenv] 
---

In this post, we shall learn how to setup a virtualenv for Tryton. Any new developer
who wishes to develop on Tryton needs to know a few basic things.

<!--more-->

Tryton is not for the faint-hearted. A new person can possibly take a long time to get adjusted
to the workflow.

* Have pip/setuptools ready. Use your package manager to get pip (apt, pacman, emerge
  etc).
* Install virtualenvwrapper. It is essential for any serious Python developer.
  Follow the steps given in the virtualenvwrapper [docs](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)
  to setup everything - thing such as the `WORKON_HOME` variable.
* Now, before you make a virtualenv, make absolutely sure that you have a minimal
  set of site packages. Site packages are those Python packages that have been
  installed system-wide. Here is a list of packages that I have (via `pip freeze`) -:

  ``` bash global pip freeze
  CDApplet==1.0
  CDBashApplet==1.0
  Cython==0.20.1post0
  apt-xapian-index==0.45
  arandr==0.1.7.1
  argparse==1.2.1
  chardet==2.0.1
  colorama==0.2.5
  defer==1.0.6
  gyp==0.1
  html5lib==0.999
  mercurial==2.8.2
  psutil==1.2.1
  pycups==1.9.66
  pycurl==7.19.3
  pygobject==3.12.0
  pysmbc==1.0.14.1
  pysqlite==2.6.3
  python-apt==0.9.3.5
  python-debian==0.1.21-nmu2ubuntu2
  python-sql==0.3
  pyxdg==0.25
  requests==2.2.1
  six==1.8.0
  stevedore==1.0.0
  urllib3==1.7.1
  virtualenv==1.11.6
  virtualenv-clone==0.2.5
  virtualenvwrapper==4.3.1
  wsgiref==0.1.2
  ```
* One particular package that you will find to give you headaches during the installation
  is `pygtk`. This package cannot be installed via pip. Why? Because screw you, that's why.
  Now you have two options.
  + Follow the steps given [here](https://gist.github.com/ches/1094799) to install `pygtk` 
    inside a virtualenv. However, you will find that doing this over and over again would
    be tedious.
  + What about the package that has been installed system-wide? Could we possibly use it?
    Well, it turns out we can! The next step details on this method.  
    PS: If you don't have it installed system-wide, do it bruh. Use your favorite package manager,
    I'm not judgin'.
* If you listened to me two steps ago and didn't fall asleep - the reason I said that
  one must keep a minimal set of site packages is because these shall be incorporated
  into the virtualenv. These are the absolute bare-minimum requirements that every
  virtualenv will get. Now issue the following command in your terminal, in whichever
  directory you've readied for this purpose -:

  ``` bash [virtualenv]
  mkproject myenv
  ```

  Substitute myenv with any name you wish. And voila, you have your newly commissioned
  virtualenv.
* After the virtualenv is created, use the `toggleglobalsitepackages` switch from inside
  it to enable pygtk. Since pygtk was installed system-wide (global site packages), it gets
  incorporated into your virtualenv and you don't have to bother about it.

* What this does is create a project folder at the location specified by the `$PROJECT_HOME`
  variable, which you must have specified during your virtualenvwrapper installation. You can
  now clone your GitHub/etc repositories inside this folder and install their requirements.

* This kind of project organization allows you to easily clone the repositories
  which constitute the requirements of a particular repository and make changes in them.
  For example, `nereid-webshop` depends on `nereid-cart-b2c`. If you need to send a patch
  on the latter, you can clone it inside the project folder you created for webshop.

And that's that folks! In the next post, we shall set up Postgres as Tryton uses
Postgres databases. Following that, we shall learn how to actually install Tryton, 
both the client and the server.
  

