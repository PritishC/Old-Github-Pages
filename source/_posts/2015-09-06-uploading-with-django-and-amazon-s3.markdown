---
layout: post
title: "Uploading With Django and Amazon S3"
date: 2015-09-06 17:20:49 +0530
comments: true
categories: [django, aws]
---

In this short post, I describe how I configured Django to upload to
Amazon S3 instead of a regular file-system upload. It can be useful
for production scenarios.

<!--more-->

We will be using the `django-storages` package to make it easier to
upload to S3. It is always better not to reinvent the wheel, but if
you'd like to explore on how to do it on your own, you definitely
should!

Install via pip.

``` bash django-storages
$ pip install django-storages
$ pip freeze | grep django-storages >> requirements.txt
```

I'm assuming that you already have a virtual environment set up for your
django project, and are installing within it.

Now in my case, I've deployed my webapp to both Heroku and [AWS]({% post_url 2015-09-03-docker-is-awesome %}).
I have different settings files for both, and I wanted my S3 setup to
be respected on both configurations. To this end, we create a separate
settings file which holds the S3 settings.

``` python aws_settings.py
import os

AWS_QUERYSTRING_AUTH = False
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
MEDIA_URL = 'http://%s.s3.amazonaws.com/your-folder/' % AWS_STORAGE_BUCKET_NAME
DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
```

In your production settings file, at the bottom, add an `if` check for
production and import these settings. I do it by looking for a particular
environment variable which is set only on production.

``` python prod.py
...
...

if os.environ.get('ENV_VAR') == 'prod':
    from aws_settings import *
```

On setting `DEFAULT_FILE_STORAGE` to `S3BotoStorage`, django-storages requires
the set of AWS credentials which you plan to use to upload to an S3 bucket.
If you don't already have them, you can go to the IAM console on AWS
and generate them. These are the permissions I added to the security
group which I applied on these credentials -:

{% img /images/AWS_IAM_S3.png 'S3 Credentials Policies' %}

The primary purpose of these credentials is to allow (in my case) an
admin user to upload/delete images on an S3 bucket. We will let the
public view images, but not manipulate them in any other way, nor abuse
the system. Note the IAM ID of the credentials, as you will need it later.

{% img /images/AWS_IAM_ID.png 'IAM User ARN or ID' %}

Now head to the S3 management console on AWS and create a bucket.

You will be presented with a prompt to enter the bucket name and the region
where it should be deployed. Choose a region keeping in mind your target
audience. You are also allowed to set up logging, with a prefix which is
basically a 'folder' in which log files will be stored. (It is easier to
think of it as a folder, though that is not entirely the case)

{% img /images/AWS_S3_BUCKET_1.png 'Create A Bucket' %}

{% img /images/AWS_S3_BUCKET_2.png 'Logging Buckets' %}

Once the bucket has been created, we have to configure certain permissions
on it. This is what the Properties section of a newly created bucket
looks like -:

{% img /images/AWS_BUCKET_PROPS.png 'Bucket Permissions' %}

Let's add a permission policy to our bucket. Click on 'Edit bucket policy'
and paste the following -:

``` json bucket policy
{
	"Version": "2008-10-17",
	"Statement": [
		{
			"Sid": "",
			"Effect": "Allow",
			"Principal": {
				"AWS": "*"
			},
			"Action": "s3:GetObject",
			"Resource": [
				"arn:aws:s3:::testbucket/*",
				"arn:aws:s3:::testbucket"
			]
		},
		{
			"Sid": "",
			"Effect": "Allow",
			"Principal": {
				"AWS": "arn:aws:iam::ID_NUMBER_HERE:root"
			},
			"Action": "s3:*",
			"Resource": [
				"arn:aws:s3:::testbucket/*",
				"arn:aws:s3:::testbucket"
			]
		}
	]
}
```

This is, in effect, a combination of policies. The first part of the policy
enforces public-read, i.e., anyone can read data on the bucket. The second
part of the policy allows any action to be performed (get, put, delete),
but this is restricted to the user with the IAM ID as given. Paste the IAM
ARN/ID from earlier here, and hit Save.

In my case, I had to edit the CORS configuration, though this may not be
necessary for you. On the same Properties > Permissions section, hit the
'Edit CORS Configuration' button and paste the following -:

``` xml cors config
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>Authorization</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

This allows users from other domains to make HTTP requests (GET and POST) on
our bucket.

And there you have it. Now you can upload files to S3, and view them in
your bucket. There should be an `uploads` folder (standard django stuff)
in the bucket after your first upload.
