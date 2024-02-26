---
title: "Contributing to Parquet"
linkTitle: "Contributing to Parquet"
weight: 3
description: >
  How to contribute to Parquet
---

Pull Requests
-------------

We prefer to receive contributions in the form of GitHub pull requests. Please send pull requests against the [github.com/apache/parquet-mr](https://github.com/apache/parquet-mr) repository. If you’ve previously forked Parquet from its old location, you will need to add a remote or update your origin remote to [https://github.com/apache/parquet-mr.git](https://github.com/apache/parquet-mr.git) Here are a few tips to get your contribution in:

1.  Break your work into small, single-purpose patches if possible. It’s much harder to merge in a large change with a lot of disjoint features.
2.  Create a JIRA for your patch on the [Parquet Project JIRA](https://issues.apache.org/jira/browse/PARQUET).
3.  Submit the patch as a GitHub pull request against the master branch. For a tutorial, see the GitHub guides on forking a repo and sending a pull request. Prefix your pull request name with the JIRA name (ex: [https://github.com/apache/parquet-mr/pull/5](https://github.com/apache/parquet-mr/pull/5)).
4.  Make sure that your code passes the unit tests. You can run the tests with `mvn test` in the root directory.
5.  Add new unit tests for your code.
6.  All Pull Requests are tested automatically on [GitHub Actions](https://github.com/apache/parquet-mr/actions). [TravisCI](https://travis-ci.org/github/apache/parquet-mr) is also used to run the tests on ARM64 CPU architecture

If you’d like to report a bug but don’t have time to fix it, you can still post it to our [issue tracker](https://issues.apache.org/jira/browse/PARQUET), or email the mailing list ([dev@parquet.apache.org](mailto:dev@parquet.apache.org)).

Committers
----------

Merging a pull request requires being a comitter on the project.

How to merge a Pull request (have an apache and github-apache remote setup):

    git remote add github-apache git@github.com:apache/parquet-mr.git
    git remote add apache https://gitbox.apache.org/repos/asf?p=parquet-mr.git


run the following command

    dev/merge_parquet_pr.py


example output:

    Which pull request would you like to merge? (e.g. 34):


Type the pull request number (from [https://github.com/apache/parquet-mr/pulls](https://github.com/apache/parquet-mr/pulls)) and hit enter.

    === Pull Request #X ===
    title   Blah Blah Blah
    source  repo/branch
    target  master
    url https://api.github.com/repos/apache/parquet-mr/pulls/X

    Proceed with merging pull request #3? (y/n):


If this looks good, type `y` and hit enter.

    From gitbox.apache.org:/repos/asf/parquet-mr.git
    * [new branch]      master     -> PR_TOOL_MERGE_PR_3_MASTER
    Switched to branch 'PR_TOOL_MERGE_PR_3_MASTER'

    Merge complete (local ref PR_TOOL_MERGE_PR_3_MASTER). Push to apache? (y/n):


A local branch with the merge has been created. Type `y` and hit enter to push it to apache master

    Counting objects: 67, done.
    Delta compression using up to 4 threads.
    Compressing objects: 100% (26/26), done.
    Writing objects: 100% (36/36), 5.32 KiB, done.
    Total 36 (delta 17), reused 0 (delta 0)
    To gitbox.apache.org:/repos/asf/parquet-mr.git
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


For now just say `n` as we have 1 branch

Website
-------
### Release Documentation

To create documentation for a new release of `parquet-format` create a new <releaseNumber>.md file under `content/en/blog/parquet-format`. Please see existing files in that directory as an example.

To create documentation for a new release of `parquet-mr` create a new <releaseNumber>.md file under `content/en/blog/parquet-mr`. Please see existing files in that directory as an example.

### Website development and deployment

#### Staging

To make a change to the `staging` version of the website:
1. Make a PR against the `staging` branch in the repository
2. Once the PR is merged, the `Build and Deploy Parquet Site`
job in the [deployment workflow](https://github.com/apache/parquet-site/blob/staging/.github/workflows/deploy.yml) will be run, populating the `asf-staging` branch on this repo with the necessary files.

**Do not directly edit the `asf-staging` branch of this repo**

#### Production

To make a change to the `production` version of the website:
1. Make a PR against the `production` branch in the repository
2. Once the PR is merged, the `Build and Deploy Parquet Site`
job in the [deployment workflow](https://github.com/apache/parquet-site/blob/production/.github/workflows/deploy.yml) will be run, populating the `asf-site` branch on this repo with the necessary files.

**Do not directly edit the `asf-site` branch of this repo**
