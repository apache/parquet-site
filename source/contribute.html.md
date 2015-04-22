#How To Contribute

## Pull Requests

We prefer to receive contributions in the form of GitHub pull requests. Please send pull requests against the [github.com/apache/incubator-parquet-mr](https://github.com/apache/incubator-parquet-mr) repository. If you've previously forked Parquet from its old location, you will need to add a remote or update your origin remote to https://github.com/apache/incubator-parquet-mr.git
Here are a few tips to get your contribution in:

  1. Break your work into small, single-purpose patches if possible. It’s much harder to merge in a large change with a lot of disjoint features.
  2. Create a JIRA for your patch on the [Parquet Project JIRA](https://issues.apache.org/jira/browse/PARQUET).
  3. Submit the patch as a GitHub pull request against the master branch. For a tutorial, see the GitHub guides on forking a repo and sending a pull request. Prefix your pull request name with the JIRA name (ex: https://github.com/apache/incubator-parquet-mr/pull/5).
  4. Make sure that your code passes the unit tests. You can run the tests with `mvn test` in the root directory. 
  5. Add new unit tests for your code. 

If you’d like to report a bug but don’t have time to fix it, you can still post it to our [issue tracker](https://issues.apache.org/jira/browse/PARQUET), or email the mailing list (dev@parquet.incubator.apache.org).

## Committers

Merging a pull request requires being a comitter on the project.

How to merge a Pull request (have an apache and github-apache remote setup):

	git remote add github-apache git@github.com:apache/incubator-parquet-mr.git
	git remote add apache https://git-wip-us.apache.org/repos/asf/incubator-parquet-mr.git

run the following command

	dev/merge_parquet_pr.py

example output:

	Which pull request would you like to merge? (e.g. 34):

Type the pull request number (from https://github.com/apache/incubator-parquet-mr/pulls) and hit enter.

	=== Pull Request #X ===
	title	Blah Blah Blah
	source	repo/branch
	target	master
	url	https://api.github.com/repos/apache/incubator-parquet-mr/pulls/X

	Proceed with merging pull request #3? (y/n): 

If this looks good, type y and hit enter.

	From git-wip-us.apache.org:/repos/asf/incubator-parquet-mr.git
	* [new branch]      master     -> PR_TOOL_MERGE_PR_3_MASTER
	Switched to branch 'PR_TOOL_MERGE_PR_3_MASTER'

	Merge complete (local ref PR_TOOL_MERGE_PR_3_MASTER). Push to apache? (y/n):

A local branch with the merge has been created. type y and hit enter to push it to apache master

	Counting objects: 67, done.
	Delta compression using up to 4 threads.
	Compressing objects: 100% (26/26), done.
	Writing objects: 100% (36/36), 5.32 KiB, done.
	Total 36 (delta 17), reused 0 (delta 0)
	To git-wip-us.apache.org:/repos/asf/incubator-parquet-mr.git
	   b767ac4..485658a  PR_TOOL_MERGE_PR_X_MASTER -> master
	Restoring head pointer to b767ac4e
	Note: checking out 'b767ac4e'.

	You are in 'detached HEAD' state. You can look around, make experimental
	changes and commit them, and you can discard any commits you make in this
	state without impacting any branches by performing another checkout.

	If you want to create a new branch to retain commits you create, you may
	do so (now or later) by using -b with the checkout command again. Example:

	  git checkout -b new_branch_name

	HEAD is now at b767ac4... Update README.md
	Deleting local branch PR_TOOL_MERGE_PR_X
	Deleting local branch PR_TOOL_MERGE_PR_X_MASTER
	Pull request #X merged!
	Merge hash: 485658a5

	Would you like to pick 485658a5 into another branch? (y/n):

For now just say n as we have 1 branch

## Website

We use middleman to generate the website content from markdown and other 
dynamic templates. The following steps assume you have a working 
ruby environment setup

	gem install bundler
	bundle install

### Checking out the website
Checkout the website from SVN:

	svn co https://svn.apache.org/repos/asf/incubator/parquet

### Make changes in source/
Make any changes in the source directory:

	cd site/source/
	vim contribute.html.md

### Generating the website
To generate the static wesbite for Apache Parquet run the following commands at the root site directory:

	bundle exec middleman build
	svn add *
	svn commit -m 'made changes to the site'

### Live Development 
Live development of the site enables automatic reload when changes are saved. 
To enable run the following command and then open a browser and navigate to 
[http://localhost:4567](http://localhost:4567/) 

	bundle exec middleman 

### Publishing the Site
The website uses svnpubsub. The publish folder contains the websites content
and when committed to the svn repository it will be automatically deployed to 
the live site. 

