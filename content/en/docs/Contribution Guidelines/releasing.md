---
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

title: "Releasing Parquet-Java"
linkTitle: "Releasing Parquet-Java"
weight: 4
description: >
  How to release Parquet-Java
---

### Overview

Parquet-Java releases are run with three GitHub Actions workflows in
[apache/parquet-java](https://github.com/apache/parquet-java/actions). The
workflows tag the release, stage and publish the Maven artifacts in Nexus,
stage the source tarball on dist.apache.org, create the GitHub releases, and
write the e-mails for the release manager to send.

| Workflow | When to run it |
| --- | --- |
| **Release - Prepare RC** | To create a release candidate |
| **Release - Cancel RC** | When a vote fails |
| **Release - Publish After Vote** | When a vote passes |

To run a workflow, open the [Actions tab](https://github.com/apache/parquet-java/actions),
select the workflow, click **Run workflow**, and fill in the inputs. Always run
the workflows from `master`. The Prepare RC and Publish workflows find the
`parquet-X.Y.x` release branch from the version and check it out themselves.

Every workflow has a **Dry run** input, which is selected by default. A dry
run prints each command without running it. Always do a dry run first, read
its summary, and then run the workflow again with **Dry run** cleared.

Each run writes its results, the next steps, and any e-mail text to the run's
**Summary** page. Keep the summary of the Prepare RC run: the Publish and
Cancel workflows need the Nexus staging repository ID from it.

N.B. These workflows release parquet-java only. The mechanics of releasing
parquet-format (keys, branches, votes) are the same, but its steps are manual.

### Setup

You will need:

- Write access to apache/parquet-java, to run the workflows.
- PMC membership, or a PMC member to help you, for the final step on
  dist.apache.org. The workflow credentials can write only to
  `dist/dev/parquet`; moving a release into `dist/release/parquet` needs a
  PMC member's SVN credentials.

The workflows use credentials stored as repository secrets:
`PARQUET_GPG_PRIVATE_KEY` signs the release, `NEXUS_STAGE_DEPLOYER_USER` and
`NEXUS_STAGE_DEPLOYER_PW` deploy to [Nexus](https://repository.apache.org/),
and `PARQUET_SVN_DEV_USERNAME` and `PARQUET_SVN_DEV_PASSWORD` write to
`dist/dev/parquet`.

The workflows sign releases with the project's automated release signing key,
which is published in [KEYS](https://downloads.apache.org/parquet/KEYS):

```
pub   rsa4096 2026-08-31 [SC]
      DD1E 0FA3 56E5 268B E450  B2AA A528 E51B CE01 BCFE
uid   Apache Parquet Automated Release Signing <private@parquet.apache.org>
```

### Release process

#### 0\. Before you start the release process

1. Verify that the release is finished (no planned Issues/PRs are pending [on the milestone](https://github.com/apache/parquet-java/milestones)).
2. For a patch release, backport the fixes to the `parquet-X.Y.x` branch.
3. Make sure CI passes on the commit you will release. The workflow stops if it does not.

#### 1\. Run "Release - Prepare RC"

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | Yes | | The release version, for example `1.18.0`. |
| `rc_number` | No | Next free RC number | The RC number. Set it only to override the next free number; the workflow stops if the RC tag already exists. |
| `dry_run` | No | Selected | Print each command without running it. |

For a new minor release, the workflow creates the `parquet-X.Y.x` release
branch from `master`. For a patch release, it uses the existing
`parquet-X.Y.x` branch.

The workflow:

1. Creates the `parquet-X.Y.x` branch, if it does not exist, and checks it out.
2. Finds the next RC number.
3. Verifies that CI passes on the release commit.
4. Sets the POM version to the release version and commits it.
5. Creates the RC tag, for example `apache-parquet-1.18.0-rc0`.
6. Deploys the artifacts to a Nexus staging repository, then closes and verifies it.
7. Builds and signs the source tarball, and writes its SHA-512 checksum.
8. Stages the tarball, signature, and checksum in
   [dist/dev/parquet](https://dist.apache.org/repos/dist/dev/parquet/).
9. Pushes the RC tag and creates a GitHub pre-release with generated release notes.
10. Writes the VOTE e-mail in the run summary.

Write down the **Nexus staging repository ID** from the summary, for example
`orgapacheparquet-1234`.

#### 2\. Review the pre-release notes

Open the [pre-release](https://github.com/apache/parquet-java/releases) that
the workflow created. You can curate the generated notes: remove unrelated
changes (whitespace, test-only changes) and sort them to make them easier to
read.

#### 3\. Send the VOTE e-mail to [dev@parquet.apache.org](mailto:dev@parquet.apache.org)

Copy the VOTE e-mail from the run summary. Add a summary of the important
changes in the release, and make sure everything in the e-mail applies to
your release.

### If the vote fails

Run **Release - Cancel RC** with these inputs:

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | Yes | | The release version, for example `1.18.0`. |
| `rc_number` | Yes | | The RC number that failed the vote, for example `0`. |
| `staging_repo_id` | Yes | | The Nexus staging repository ID from the Prepare RC summary, for example `orgapacheparquet-1234`. |
| `allow_description_mismatch` | No | Cleared | Skip the check that the staging repository description is `Apache Parquet <VERSION> RC<NUM>`. Use it only for recovery, when the description was changed by hand. |
| `dry_run` | No | Selected | Print each command without running it. |

Before it drops the staging repository, the workflow verifies that the
repository belongs to `org.apache.parquet`, is closed, contains the release
version, and has the expected description.

The workflow drops the Nexus staging repository, removes the RC from
`dist/dev/parquet`, and writes the vote result e-mail in the run summary. Fill
in the reason the vote failed and send the e-mail to the dev list.

The RC tag and the GitHub pre-release stay in place, so the RC number is not
used again. After the issues are fixed, run Prepare RC again; it uses the next
RC number.

### Publishing after the vote passes

#### 1\. Send the vote result e-mail

Send a `[RESULT][VOTE] Release Apache Parquet <VERSION> RC<NUM>` e-mail to the
dev list with the vote counts.

#### 2\. Run "Release - Publish After Vote"

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | Yes | | The release version, for example `1.18.0`. |
| `rc_number` | No | Latest RC | The RC number that passed the vote. It must be the latest RC for the version. |
| `staging_repo_id` | Yes | | The Nexus staging repository ID from the Prepare RC summary, for example `orgapacheparquet-1234`. |
| `allow_description_mismatch` | No | Cleared | Skip the check that the staging repository description is `Apache Parquet <VERSION> RC<NUM>`. Use it only for recovery, when the description was changed by hand. |
| `dry_run` | No | Selected | Print each command without running it. |

Before it changes anything, the workflow verifies that the staging repository
belongs to `org.apache.parquet`, is closed, contains the release version, and
has the description `Apache Parquet <VERSION> RC<NUM>`. It also checks out the
`parquet-X.Y.x` branch and verifies that its head is the RC commit. The
workflow then:

1. Creates the final release tag, for example `apache-parquet-1.18.0`, on the RC commit.
2. Releases the Nexus staging repository to Maven Central.
3. Pushes the release tag and creates the GitHub release.
4. Sets the next development version, for example `1.18.1-SNAPSHOT`, on the
   release branch and pushes it.
5. Writes the remaining manual steps and the ANNOUNCE e-mail in the run summary.

#### 3\. Move the release on dist.apache.org (PMC member)

The run summary has a block of `svn` commands for the release. A PMC member
copies the block and runs it with their own SVN credentials. The commands:

- Move the RC from `dist/dev/parquet` to `dist/release/parquet`.
- Remove older patch releases of the same minor version that the new release
  replaces. Releases of other minor versions are not changed.

For example, for 1.14.3:

```sh
svn mv https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.14.3-rc0 \
  https://dist.apache.org/repos/dist/release/parquet/apache-parquet-1.14.3 \
  -m "Release Apache Parquet 1.14.3"
svn rm https://dist.apache.org/repos/dist/release/parquet/apache-parquet-1.14.2 \
  -m "Remove old release apache-parquet-1.14.2 (superseded by 1.14.3)"
```

Removed releases stay available on [archive.apache.org](https://archive.apache.org/dist/parquet/).

#### 4\. Update parquet.apache.org

Update the downloads page on parquet.apache.org and add a release blog post.
The run summary has a template for the blog post. Instructions for updating
the site are on the [contribution page](https://parquet.apache.org/docs/contribution-guidelines/contributing/).

#### 5\. Send the ANNOUNCE e-mail to [announce@apache.org](mailto:announce@apache.org) and the dev list

Copy the ANNOUNCE e-mail from the run summary. The e-mail links to the
downloads page, so send it after the release is on
[downloads.apache.org](https://downloads.apache.org/parquet/) and the site is updated.

#### 6\. Update parquet-format with feature enablement guidance

The recommendations for other feature enablement is generally tied to releases of
parquet-java (details are in the parquet-format repo).  As releases are made the
specification should be updated to indicate the recommended dates for when a new
feature may be enabled.

### Running the release scripts locally

Each workflow runs a script in
[`release/bin`](https://github.com/apache/parquet-java/tree/master/release/bin)
of parquet-java. You can run the scripts on your own machine, for example to
debug a failed run. See the
[release README](https://github.com/apache/parquet-java/blob/master/release/README.md)
for details.

### Release Cadence

Provided enough volunteers are available the Parquet community aims to have
releases on a quarterly basis (Targets months are January, April, July and
October). If a new major version is necessary it will be targetted for the
October release.

### Release Verification

The Apache Parquet Release Approval process follows the guidelines defined at the
Apache Software Foundation [Release Approval](https://www.apache.org/legal/release-policy.html#release-approval) page.

For a release vote to pass, a minimum of three positive binding votes and more
positive binding votes than negative binding votes MUST be cast.
Releases may not be vetoed. Votes cast by PMC members are binding, however,
non-binding votes are greatly encouraged and a sign of a healthy project.

In order to cast a vote individuals are expected to follow the following steps.

#### Download source package, signature file, hash file and KEYS

The Release candidate will be present at `https://dist.apache.org/repos/dist/dev/parquet/`.
The RC folder will depend on the version and the release candidate id. See the following example files for
Apache Parquet 1.15.0 RC 1:
```
wget https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.15.0-rc1/apache-parquet-1.15.0.tar.gz
wget https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.15.0-rc1/apache-parquet-1.15.0.tar.gz.asc
wget https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.15.0-rc1/apache-parquet-1.15.0.tar.gz.sha512
wget https://dist.apache.org/repos/dist/release/parquet/KEYS
```

#### Verify signature and hash

GnuPG is recommended, which can be install by:
- `yum install gnupg` or `apt-get install gnupg` on Linux based environments.
- `brew install gnupg` on macOS environments.

```
gpg --import KEYS
gpg --verify apache-parquet-1.15.0.tar.gz.asc apache-parquet-1.15.0.tar.gz
sha512sum --check apache-parquet-1.15.0.tar.gz.sha512
```

#### Verify license header

Apache RAT is recommended to verify the license header, which can be dowload with the following command.

```
wget https://archive.apache.org/dist/creadur/apache-rat-0.16.1/apache-rat-0.16.1-bin.tar.gz
tar zxvf apache-rat-0.16.1-bin.tar.gz
```

You can check with the following command. The current command uses a regular expression to avoid raising false
positives for some files.

The command will output a summary, the list of files with their licenses and any file that does not contain a valid license header.

```
java  -jar apache-rat-0.16.1/apache-rat-0.16.1.jar -a -d apache-parquet-1.15.0.tar.gz -e  "\w+.avsc$|\w+\-2.parquet$|.gitignore|PULL_REQUEST_TEMPLATE.md"
```

#### Verify building and tests

Check the [building section](https://github.com/apache/parquet-java/blob/master/README.md#building) on the
[parquet-java](https://github.com/apache/parquet-java) repository.
