---
layout: post
title: "Development Cheatsheet @ Openlabs"
date: 2015-01-25 11:12:33 +0530
comments: true
categories: [github, openlabs] 
---

The target audience of this article is the new arrivals at our company, and I
will try to make it as easy as possible on them. This assumes a basic knowledge
of Git/GitHub (and also knowing the difference between the two) and will follow
a scenario-based approach.

<!--more-->

## Ground Zero: Install ZSH/Oh-My-ZSH

This should be done before anything else, mainly because ZSH is an awesome shell
and is very customizable. Here's a screenshot of my ZSH shell (I use the cloud
theme) -:

<img src="{{ root_url }}/images/zsh.png" />

Note how the branch name is shown in square-brackets and the lightning symbol
signifies that a change has occurred in some file(s) which may or may not be
committed.

``` bash zero
$ sudo apt-get install zsh curl
Installing...
$ curl -L https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh | sh
Installing... (you may be prompted to answer a few questions)
```

Once the install is complete, close your current command prompt and re-open it.
You should now be using ZSH. You can customize your configuration by editing
the `.zshrc` file, which is present at the home folder (`$HOME`). I'll leave
that bit out to the reader to experiment with stuff like themes.

## Scenario-I: Basic Git Setup.

To begin working on one of the company repositories, first fork the repo on GitHub
and then use the following commands on your terminal (assuming your SSH keys
have already been setup) -:

``` bash scenario-I
$ git clone git@github.com:<your-username>/<repo-name>
Cloning...
$ cd <repo-name>
$ git remote add openlabs git@github.com:openlabs/<repo-name>
```

You can run `git remote -vv` to check the names of your remotes. At this point,
you should have the remotes 'origin' and 'openlabs' for your cloned repository.

## Scenario-II: Writing A Feature/Hotfix

All work is usually based off of the develop branch, and so, you will checkout
your new branch off develop. There may be cases when you will have to checkout
off a version branch - that is described in the next scenario.

You can prefix your branch name with 'feature' or 'fix' depending on whether
it is a feature to be added or a fix to be made. Branch naming is completely
your choice, I only try provide a useful convention here.

For example, you wish to add a feature and your task ID is 0000. You will do so
as follows -:

``` bash scenario-II
$ git branch
* develop
$ git checkout -b feature/task-0000
```

Now you're on the `feature/task-0000` branch, as the ZSH branch indicator should
tell you. You can do some work, and then commit it.

``` bash scenario-II
$ git status
Shows files which are being tracked, are staged for commit or are not staged.
$ gst
Shorthand for the above which works with zsh.
$ git add <filenames>
$ git commit
Write your commit message and use VI shortcuts to save the message, i.e., :wq
If you have nano configured as your editor instead, use that.
Commit messages should be brief yet descriptive, and neatly written.
$ git config --global push.simple
Needs to be set only once.
$ git push -uvf origin
This pushes your current branch to the origin remote (which is your fork).
```

Now you can open a pull request from GitHub on the openlabs remote. Make sure
to get your work reviewed.

## Scenario-IIA: Writing A Feature For Version Branches

Sometimes, you may need to write features not for develop but for an earlier
version branch. In this case, you may do a `git fetch openlabs` to get the branch
data as is required. For example, some of our repositories are being moved to
v3.4, which becomes the develop branch. v3.2 gets a branch named `3.2`.

In this case, you need to checkout off of the 3.2 branch instead of develop, and
your PR should be sent on the 3.2 branch. The commands are the same, except
the branch you are checking out off changes.

## Scenario-III: Rebase To Keep Up

Rebasing is an important part of using git repositories. In a team environment,
you will have to rebase often to keep up with the latest changes, as you will
not be the only one pushing features and fixes to the openlabs remote.

It is advisable that before you checkout off of develop, you should do a rebase
as follows -:

``` bash scenario-III
$ git pull --rebase openlabs branch:branch
Rebasing...
May or may not introduce merge conflicts.
```

`branch` here may either be develop or a version branch, as was explained earlier.

To resolve merge conflicts, you will need to search for files which have the
`>>>HEAD` symbol appearing in them. I usually do this with the `grep` command.
Take a look at the latest version of the files from GitHub and modify your 
local files accordingly. Be careful not to omit any code that was not added by
you.

Once you are done editing your local files, do a `git add` on them, and then run
`git rebase --continue`.

## Bonus Scenario: Protect Your Slack/HipChat From Attack!

One of the fun parts of being at Openlabs is that we advise our colleagues
not to leave their systems unlocked. If you leave your system on, you are fair
game for us :D.

Leaving your system on may or may not lead to one of the following -:

* Silly messages appearing on your HipChat/Slack, on the Water Cooler.
* Declarations of coming out of the closet on your Facebook (if we know you well
enough).
* Messed up configurations, and so on.

Vanilla Ubuntu users can use the Ctrl+L shortcut to lock their systems quickly.
For those who cannot use this shortcut for whatever reason (for example, Lubuntu
does not have such a shortcut), they may install `xscreensaver` using their
package manager and use this little script I made -:

{% include_code sample .logoutscript lang:bash .logoutscript %}

`grep` returns useful exit codes which can be used to find out whether `xscreensaver`
is running or not. If it is not running, it is made to run. Henceforth, the
lock command is applied.

You may save this script to your home directory and then run `sh ~/.logoutscript`
whenever you need to get away from your system!

PS: I will update this as more use cases come to mind.
