---
layout: post
title: "Overcoming SD Card Write Restrictions"
date: 2014-10-24 13:19:42 +0530
comments: true
categories: [android, kitkat] 
---

I think all of us have encountered the SD card write restrictions on Android 
KitKat devices at some time or the other. What makes it really annoying is that
it is necessary for security, and cannot be bypassed without root access.

<!--more-->

What I am going to propose here is a kind of long hack. One needs some knowledge
of SSH/SCP file transfers to attempt this procedure.

(If you have a SD card reader, you could just use that instead)

First of all, install the [SSHDroid](https://play.google.com/store/apps/details?id=berserker.android.apps.sshdroid&hl=en) app on your device.
This allows you to run a SSH server on your device, which can be accessed from
your computer. Once this is done, just open the app to start running the server.

It should look something like this -:

<img src="{{ root_url }}/images/sshdroid.png"/>

If you are on Linux, fire up your file manager (Nautilus/PCManFM/etc), and search
for the option to connect to a server. For example, PCManFM has the following -:

<img src="{{ root_url }}/images/pcmanfm.png"/>

Choose the SSH/SFTP protocol, enter the server details, and connect to the server.
The default credentials are `root` and password `admin`. Now look for the path
`/sdcard` or `/sdcard0`. This is a symlink to the internal memory of the Android
device.

Now the procedure is simple: copy/move all the files that you wish to move to the SD
card to your PC (which is connected to the SSH server). Once you are done, close
the connection. Now connect your device via USB to get access to the SD card.
Copy all your files to the SD card from your PC.

And there you have it! Admittedly this is a bit long, but for someone used to
doing it all the time, it wasn't much of a problem for me. If you are even more
terminal savvy, I would suggest keeping the device connected via USB the whole
time, and using the terminal (scp command) to transfer files directly to the SD
card from the internal memory (I haven't tested this as of yet).

Or you could just root. That too.


