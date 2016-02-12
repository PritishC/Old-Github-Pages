---
layout: post
title: "Tryton Module Basics and Programming Example"
date: 2014-11-02 19:22:17 +0530
comments: true
categories: [tryton]
---

This article will cover the basics of developing a module for Tryton. After having
gone through the setup, it is finally time to make your own module. This might
turn out to be a longer post than all my previous ones, so hang in there.

*Note*: This article is to some extent *deprecated* - it was written with Tryton
v3.2 in mind.

<!--more-->

## Introduction

I will use the [module](https://github.com/PritishC/nereid-erms/tree/develop) I developed as part of an initial assignment to explain. 
The Tryton [documentation](http://docs.tryton.org/) tells us that the basic 
components of a Tryton module are its models and its views.

The models define the backend of the application. Much like in any other ORM, they
will map to tables in a database, which in this case is controlled by the Postgres
server. The views are written in XML and they define what the user sees in the
Tryton client. Views can even be inherited and this makes for a very clever design -
_it supports reusability_.

Each model can have a set of fields - similar to that of a table in a DB. The fields can have types such as Integer, Char, Text, etc. as well as special relationship
types such as Many2One and One2Many. Refer the docs for more information.

Each view is defined in the view directory and these views are brought together
in a ModelName.xml file which is at the project's root.

Now suppose we wish to build an Employee Record Management system in Tryton. The
first thing to do is to design the models, and then we would go about designing
the views. I designed models for an Employee, a Department and a Designation.

## The Models

One may choose to have a model be stand-alone or be 'part' of another model.
Tryton also has an easy mechanism for models which need to be customized in down-
stream modules, similar to inheritance. For example, I know that the Employee
model is already present in Tryton with the `__name__` set as `company.employee`. 
I wish to customize this model and I have done so as follows -:

{% include_code employee.py lang:python erms/employee.py %}

There's a lot going on here, so let's take it step by step. We can see two models
that we wish to be in the Employee 'namespace', `Employee` and `Designation`.
If you think about it, after all, it is an employee who has a designation!

Our first field in `Employee` is a selection field - the user can select from the
options that we present to them. The options are written as a list of two-tuples.
Each two-tuple is of the format `(option_name, option_string)`.

The other options provided to the field type constructor are the name of the field
to be displayed, the option of making the field mandatory or required, the possible
states of the field and other fields that this one may depend on. We'll get to
`states` and `depends` in a moment.

The next field is an interesting one - it defines a many to one relationship to
the `Department` model. This means that multiple employees can belong to a single
department. The constructor arguments are quite simple to grasp - the `__name__`
of the model being related with, the string to be displayed, and so on.

The third field - `designation` - is very similar to `department`. The only difference 
here is that we have also set a domain argument. Domains are lists of three-tuples
that can be used to form a particular selection over the records of a model.
In this case, we wish to comb through the records of a designation and select
those which belong to the department specified by the field `department`.`Eval`
is a PYSON statement which gives us a boolean value. Domains are used alot when 
searching records, and they contain [`PYSON`](http://doc.tryton.org/3.4/trytond/doc/topics/pyson.html#topics-pyson) statements.

Since we have just covered PYSON, we may as well check out those global variables
now - `STATES` and `DEPENDS`. The former is a dict whose keys are state names,
and whose values are PYSON statements. In this case, the `readonly` state is
activated if we find that the `active` field of the model has been set to false.

The rest of the fields are simple Char fields and I shall not cover them in detail.

Let us come down to the remaining parts of the `Employee` class. `_sql_error_messages`
is a dict whose keys are names of error messages and whose values are the strings
to be displayed in case such an error occurs. `_unique` is a list of three-tuples
which define some uniqueness constraints on the model table.

The `__setup__` method is an incredibly useful classmethod. Note how I am updating
the `party` and `company` fields of our custom Employee class (these fields are
present in the parent Employee model, and thus, need to have their `states` and
`depends` set, for which I have made a method) here - these fields need not be
rewritten here. I am also setting the SQL constraints of the table here. All sorts
of field updation and customization can be done in `__setup__`.

The `default` methods are pretty self-explanatory - they return default values
for a field. We also have methods such as `on_change` and `on_change_with` -
they are quite interesting and one should browse the docs to see what they do.

Let's cover one more model class - `Department`. It has a Many2One field relating 
it to the `Company` class. One may check that out here -:

{% include_code company.py lang:python erms/company.py %}

Note how model classes that are new to the hierarchy have to specifically inherit
from classes such as `ModelSQL`, but classes which are already present and are
being customized - such as `Employee` - need not have this explicit inheritance.
The `__name__` field does this magic for us.

Now the `Department` is a part of the `Company` model. It has a Many2One field
relating it to `Company`. How must we obtain the company that this department
is associated with, or more precisely, the _active record_ of the `Company` model,
for our default method?

We do so by looking for it in the transaction context. `context` is a dict which
has such keys.

And that wraps up model basics! Let us now move to views.

## The Views

Let's check out the view for our `Employee` model. The root xml is as follows -:

{% include_code employee.xml lang:xml erms/employee.xml %}

Views can be of two main types - tree and form. Form views are used to enter 
data while tree views are used to display them. The first two record tags deal 
with, in a sense, instances of the model class with the `__name__` `ir.ui.view`. 
The first is for a tree and the second for a form. Note how they are inheriting 
from tree and form views which are already present in the parent Employee model.

The `menuitem` tag allows us to create a new menu item for an existing menu. In
this case, we add `Employees` to the `Party` menu. `company.act_employee_form` is
predefined in the parent model and we need not worry about defining it. act stands
for "action", and the action here is to open the form view.

We may have to define our form and tree views separately, especially if they are
inheriting from a parent model, to add any extra details, or just to create from
scratch. For example, here are the form and tree views which were defined in the
employee xml -:

{% include_code form view lang:xml erms/view/employee_form.xml %}

{% include_code tree view lang:xml erms/view/employee_tree.xml %}

These views use the newer xpath syntax that the Tryton community has incorporated.
In effect, the xpath statement here tells Tryton to put our custom Employee fields
after the company field. The active field is designated as a checkbox by putting
it in a group for checkboxes.
The `notebook` tag allows one to create tabs in the form view which can be used
to categorize or classify details according to some criterion. Notebooks have
pages which contain fields in a particular category. For example, we have two pages - 
`General Details` and `Personal Details`. The form view needs a label to show in
Tryton for each field name. The tree view needs no such thing.

Also, note how the `designation` and `department` fields are defined as selection
widgets. They will appear as drop-down menus in Tryton, and the values in these
menus will correspond to the list of active records for the `Designation` and
`Department` models, if the user has created any. I would recommend checking out
the other views at my project's github page. 

Now we are left with module boilerplate and installation.

## Module Installation

We have the raw materials for our Tryton module - but we still have no idea how
to set things up and finally install the module. My colleagues over at the company
have created a nifty command-line application which automates the process - it
can be found [here](https://github.com/openlabs/trytond-cookiecutter).

In your project's root directory, clone the cookiecutter module as is given in
the readme. We will be prompted to enter project configuration details, and these
may be changed anytime by modifying `cookiecutter.json`.

Once this is done, we can install our Tryton module's various dependencies and 
write the module to the `trytond/modules` directory by running the following
command - `python setup.py install`. We have our Tryton database which we created
earlier - we shall install the module using this DB.

``` bash installing your module
$ trytond -c path/to/trytond.conf -i module_name -d db_name
```

One should replace module_name with 'all' for first time installation. The -i
option can be replaced with -u to update a particular module. Module updation is
usually done when we change or add a model(s) in that module.

And now we should have a fully functional module in Tryton. Check it out by running
the Tryton client. 

I hope everyone enjoyed reading this post as much as I did writing it. Until
next time then.
