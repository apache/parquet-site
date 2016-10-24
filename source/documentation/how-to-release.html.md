
## How to release

### Setup

You will need:
* PGP code signing keys, published in KEYS
* Permission to stage artifacts in Nexus

Make sure you have permission to deploy Parquet artifacts to Nexus by pushing a snapshot:

```
mvn deploy
```

If you have problems, read the [publishing Maven artifacts documentation][publish-maven-docs]

[publish-maven-docs]: https://www.apache.org/dev/publishing-maven-artifacts.html

### Release process

Parquet uses the maven-release-plugin to tag a release and push binary artifacts to staging in Nexus. Once maven completes the release, the offical source tarball is built from the tag.

Before you start the release process:

1. Verify that the release is finished (no planned JIRAs are pending)
2. Build and test the project
3. Update the change log
  * Go to the release notes for the release in JIRA
  * Copy the HTML and convert it to markdown with an [online converter][html-to-md]
  * Add the content to CHANGES.md and update formatting
  * Commit the update to CHANGES.md

[html-to-md]: https://domchristie.github.io/to-markdown/

#### 1. Run the prepare script

```
sh dev/prepare-release.sh <version>
```

This runs maven's release prepare with a consistent tag name. After this step, the release tag will exist in the git repository.

If this step fails, you can roll back the changes by running these commands.

```
find ./ -type f -name '*.releaseBackup' -exec rm {} \;
find ./ -type f -name 'pom.xml' -exec git checkout {} \;
```

#### 2. Run release:perform to stage binaries

```
mvn release:perform
```

This uploads binary artifacts for the release tag to [Nexus][nexus].

#### 3. In Nexus, close the staging repository

Closing a staging repository makes the binaries available in [staging][staging], but does not publish them.

1. Go to [Nexus][nexus].
2. In the menu on the left, choose "Staging Repositories".
3. Select the Parquet repository.
4. At the top, click "Close" and follow the instructions. For the comment use "Apache Parquet [Format] <VERSION> <RC>".

#### 4. Run the source tarball script

```
sh dev/source-release.sh <version> <rc-number>
```

This script builds the source tarball from the release tag's SHA1, signs it, and uploads the necessary files with SVN.

The source release is pushed to https://dist.apache.org/repos/dist/dev/parquet/

The last message from the script is the release commit's SHA1 hash and URL for the VOTE e-mail.

#### 5. Send a VOTE e-mail to dev@parquet.apache.org

Here is a template you can use. Make sure everything applies to your release.

```
Subject: [VOTE] Release Apache Parquet <VERSION> RC<NUM>
```
```
Hi everyone,

I propose the following RC to be released as official Apache Parquet <VERSION> release.

The commit id is <SHA1>
* This corresponds to the tag: apache-parquet-<VERSION>
* https://github.com/apache/parquet-format/tree/<SHA1>
* https://git-wip-us.apache.org/repos/asf/projects/repo?p=parquet-mr.git&a=commit&h=<SHA1>

The release tarball, signature, and checksums are here:
* https://dist.apache.org/repos/dist/dev/parquet/<PATH>

You can find the KEYS file here:
* https://dist.apache.org/repos/dist/dev/parquet/KEYS

Binary artifacts are staged in Nexus here:
* https://repository.apache.org/content/groups/staging/org/apache/parquet/parquet/

This release includes important changes that I should have summarized here, but I'm lazy.

Please download, verify, and test.

Please vote by <72 HOUR FROM NOW>

[ ] +1 Release this as Apache Parquet <VERSION>
[ ] +0
[ ] -1 Do not release this because...

```


[nexus]: https://repository.apache.org/
[staging]: https://repository.apache.org/content/groups/staging/org/apache/parquet/

### Publishing after the vote passes

After a release candidate passes a vote, the candidate needs to be published as the final release.

#### 1. Release the binary repository in Nexus


#### 2. Copy the release artifacts in SVN into releases

First, check out the candidates and releases locations in SVN:

```
mkdir parquet
cd parquet
svn co https://dist.apache.org/repos/dist/dev/parquet candidates
svn co https://dist.apache.org/repos/dist/release/parquet releases
```

Next, copy the directory for the release candidate the passed from candidates to releases and rename it; remove the "-rcN" part of the directory name.

```
cp -r candidates/apache-parquet-<VERSION>-rcN/ releases/apache-parquet-<VERSION>
```

Then add and commit the release artifacts:

```
cd releases
svn add apache-parquet-<version>
svn ci -m "Parquet: Add release <VERSION>"
```


#### 3. Send an ANNOUNCE e-mail to announce@apache.org and the dev list

```
[ANNOUNCE] Apache Parquet release <VERSION>
```
```
I'm please to announce the release of Parquet <VERSION>!

Parquet is a general-purpose columnar file format for nested data. It uses
space-efficient encodings and a compressed and splittable structure for
processing frameworks like Hadoop.

Changes are listed at: <CHANGES-URL>

This release can be downloaded from: https://www.apache.org/dyn/closer.cgi/parquet/

Java artifacts are available from Maven Central.

Thanks to everyone for contributing!
```

#### 4. Update parquet.apache.org

Instructions for updating the site are on the [contribution page][parquet-site-docs].

[parquet-site-docs]: http://parquet.apache.org/contribute/


### What to do if a vote fails

If a vote fails, you need to remove the release tag that was created by the `dev/prepare-release.sh` script:

```
git tag -d apache-parquet-<VERSION> # delete locally
git push apache :apache-parquet-<VERSION> # delete in the Apache repo
```

Then, use the release process above to build another RC for the release version.

