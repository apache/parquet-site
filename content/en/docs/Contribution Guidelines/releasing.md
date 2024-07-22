---
title: "Releasing Parquet"
linkTitle: "Releasing Parquet"
weight: 4
description: >
  How to release Parquet-Java
---

### Setup

You will need: 

- PGP code signing keys, published in [KEYS](https://downloads.apache.org/parquet/KEYS).
- Permission to stage artifacts in [Nexus](https://repository.apache.org/).

Make sure you have permission to deploy Parquet artifacts to Nexus by pushing a snapshot:

```sh
mvn deploy
```

If you have problems, read the [publishing Maven artifacts documentation](https://www.apache.org/dev/publishing-maven-artifacts.html).

### Release process

Parquet uses the maven-release-plugin to tag a release and push binary artifacts to staging in Nexus. Once maven completes the release, the official source tarball is built from the tag.

Before you start the release process:

1. Verify that the release is finished (no planned Issues/PRs are pending [on the milestone](https://github.com/apache/parquet-java/milestones)) 
1. Build and test the project 
1. Create a new branch for the release if this is a new minor version. For example, if the new minor version is 1.14.0, create a new branch `parquet-1.14.x`

#### 1\. Run the prepare script

```sh
./dev/prepare-release.sh <version> <rc-number>
```

This runs maven’s release prepare with a consistent tag name. After this step, the release tag will exist in the git repository.

If this step fails, you can roll back the changes by running these commands.

```sh
find ./ -type f -name '*.releaseBackup' -exec rm {} \;
find ./ -type f -name 'pom.xml' -exec git checkout {} \;
```

#### 2\. Run release:perform to stage binaries

Upload binary artifacts for the release tag to [Nexus](https://repository.apache.org/):

```sh
mvn release:perform
```

#### 3\. In Nexus, close the staging repository

Closing a staging repository makes the binaries available in [staging](https://repository.apache.org/content/groups/staging/org/apache/parquet/), but does not publish them.

1.  Go to [Nexus](https://repository.apache.org/).
2.  In the menu on the left, choose “Staging Repositories”.
3.  Select the Parquet repository.
4.  At the top, click “Close” and follow the instructions. For the comment use “Apache Parquet \[Format\] ”.

#### 4\. Run the source tarball script

```sh
dev/source-release.sh <version> <rc-number>
```

This script builds the source tarball from the release tag’s SHA1, signs it, and uploads the necessary files with SVN.

The source release is pushed to [https://dist.apache.org/repos/dist/dev/parquet/](https://dist.apache.org/repos/dist/dev/parquet/)

The last message from the script is the release commit’s SHA1 hash and URL for the VOTE e-mail.

### 5\. Prepare the pre-release

Creating the [pre-release](https://github.com/apache/parquet-java/releases/new) will give the users the changelog to see if they need to validate certain functionality. First select the newly created `rc` (ex: `apache-parquet-1.15.0-rc0`) tag, and then the previous release (ex. `apache-parquet-1.14.1`). Hit the `Generate release notes` button to auto generate the notes. You can curate the notes a bit by removing unrelated changes (whitespace, test-only changes) and sorting them to make them easier to digest. Make sure to check the `Set as pre-release` checkbox as this is a release candidate.

#### 5\. Send a VOTE e-mail to [dev@parquet.apache.org](mailto:dev@parquet.apache.org)

Here is a template you can use. Make sure everything applies to your release.

    Subject: [VOTE] Release Apache Parquet <VERSION> RC<NUM>


    Hi everyone,

    I propose the following RC to be released as official Apache Parquet <VERSION> release.

    The commit id is <SHA1>
    * This corresponds to the tag: apache-parquet-<VERSION>-rc<NUM>
    * https://github.com/apache/parquet-mr/tree/<SHA1>

    The release tarball, signature, and checksums are here:
    * https://dist.apache.org/repos/dist/dev/parquet/<PATH>

    You can find the KEYS file here:
    * https://downloads.apache.org/parquet/KEYS

    You can find the changelog here:
    https://github.com/apache/parquet-java/releases/tag/apache-parquet-<VERSION>-rc<NUM>

    Binary artifacts are staged in Nexus here:
    * https://repository.apache.org/content/groups/staging/org/apache/parquet/

    This release includes important changes that I should have summarized here, but I'm lazy.

    Please download, verify, and test.

    Please vote in the next 72 hours.

    [ ] +1 Release this as Apache Parquet <VERSION>
    [ ] +0
    [ ] -1 Do not release this because...



### Publishing after the vote passes

After a release candidate passes a vote, the candidate needs to be published as the final release.

#### 1\. Tag final release and set development version

```sh
./dev/finalize-release <release-version> <rc-num> <new-development-version-without-SNAPSHOT-suffix>
```

This will add the final release tag to the RC tag and sets the new development version in the pom files. If everything is fine push the changes and the new tag to GitHub: `git push --follow-tags`

#### 2\. Release the binary repository in Nexus

Releasing a binary repository publishes the binaries to [public](https://repository.apache.org/content/groups/public/org/apache/parquet/).

1.  Go to [Nexus](https://repository.apache.org/).
2.  In the menu on the left, choose “Staging Repositories”.
3.  Select the Parquet repository.
4.  At the top, click Release and follow the instructions. For the comment use “Apache Parquet \[Format\] ”.

#### 3\. Copy the release artifacts in SVN into releases

First, check out the candidates and releases locations in SVN:

```sh
svn mv https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-<VERSION>-rcN/ https://dist.apache.org/repos/dist/release/parquet/apache-parquet-<VERSION> -m "Parquet: Add release <VERSION>"
```

#### 4\. Update parquet.apache.org

Update the downloads page on parquet.apache.org. Instructions for updating the site are on the [contribution page](https://parquet.apache.org/docs/contribution-guidelines/contributing/).

### 5\. Add the release to GitHub

Add a [new release to GitHub](https://github.com/apache/parquet-java/releases/new). First select the newly tag (ex: `apache-parquet-1.15.0`), and then the previous release (ex. `apache-parquet-1.14.1`). You can copy the release notes from the RC that passed the vote.

#### 6\. Send an ANNOUNCE e-mail to [announce@apache.org](mailto:announce@apache.org) and the dev list

    [ANNOUNCE] Apache Parquet release <VERSION>


    I'm please to announce the release of Parquet <VERSION>!

    Parquet is a general-purpose columnar file format for nested data. It uses
    space-efficient encodings and a compressed and splittable structure for
    processing frameworks like Hadoop.

    Changes are listed at: https://github.com/apache/parquet-java/releases/tag/apache-parquet-<VERSION>

    This release can be downloaded from: https://parquet.apache.org/downloads/

    Java artifacts are available from Maven Central.

    Thanks to everyone for contributing!
