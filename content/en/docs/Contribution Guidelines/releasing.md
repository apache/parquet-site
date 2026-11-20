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

Three GitHub Actions workflows in
[apache/parquet-java](https://github.com/apache/parquet-java/actions) run the
Parquet-Java releases. The workflows tag the release, stage and publish the
Maven artifacts in Nexus, and stage the source tarball on dist.apache.org.
They also create the GitHub releases and write the e-mails that the release
manager sends.

| Workflow | When to run it |
| --- | --- |
| **Release - Prepare RC** | To create a release candidate |
| **Release - Cancel RC** | When a vote fails |
| **Release - Publish After Vote** | When a vote passes |

To run a workflow:

1. Open the [Actions tab](https://github.com/apache/parquet-java/actions).
2. Select the workflow.
3. Click **Run workflow**.
4. Set the inputs.

Always run the workflows from `master`. The Prepare RC and Publish workflows
use the version to find the `parquet-X.Y.x` release branch. Then they check
out that branch themselves.

Each workflow has a **Dry run** input, and it is selected by default. A dry
run prints each command and does not run it. Always use this sequence:

1. Do a dry run.
2. Read the summary of the dry run.
3. Run the workflow again with **Dry run** cleared.

Each run writes its results, the next steps, and any e-mail text to the
**Summary** page of the run. Keep the summary of the Prepare RC run. The
Publish and Cancel RC workflows need the Nexus staging repository ID from it.

N.B. These workflows release only parquet-java. The steps to release
parquet-format are manual. The mechanics (keys, branches, votes) are the same.

### Setup

You will need:

- Write access to apache/parquet-java, to run the workflows.
- PMC membership, or a PMC member who helps you, for the final step on
  dist.apache.org. The workflow credentials can write only to
  `dist/dev/parquet`. A move into `dist/release/parquet` needs the SVN
  credentials of a PMC member.

The workflows use these repository secrets:

| Secret | Use |
| --- | --- |
| `PARQUET_GPG_PRIVATE_KEY` | Signs the release. |
| `NEXUS_STAGE_DEPLOYER_USER`, `NEXUS_STAGE_DEPLOYER_PW` | Deploy to [Nexus](https://repository.apache.org/). |
| `PARQUET_SVN_DEV_USERNAME`, `PARQUET_SVN_DEV_PASSWORD` | Write to `dist/dev/parquet`. |

The workflows sign releases with the key "Apache Parquet Automated Release
Signing". The [KEYS](https://downloads.apache.org/parquet/KEYS) file contains
this key:

```
pub   rsa4096 2026-08-31 [SC]
      DD1E 0FA3 56E5 268B E450  B2AA A528 E51B CE01 BCFE
uid   Apache Parquet Automated Release Signing <private@parquet.apache.org>
```

### Release process

#### 0\. Before you start the release process

1. Verify that the release is complete. No planned issues or PRs are open [on the milestone](https://github.com/apache/parquet-java/milestones).
2. For a patch release, backport the fixes to the `parquet-X.Y.x` branch.
3. Verify that CI passes on the commit that you will release. The workflow stops if CI does not pass.

#### 1\. Run "Release - Prepare RC"

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | Yes | | The release version, for example `1.18.0`. |
| `rc_number` | No | Next free RC number | The RC number. Set it only to override the next free number. The workflow stops if the RC tag already exists. |
| `dry_run` | No | Selected | Print each command and do not run it. |

For a new minor release, the workflow creates the `parquet-X.Y.x` release
branch from `master`. For a patch release, it uses the existing
`parquet-X.Y.x` branch.

The workflow:

1. Creates the `parquet-X.Y.x` branch if it does not exist, then checks out the branch.
2. Finds the next RC number.
3. Verifies that CI passes on the release commit.
4. Sets the POM version to the release version and commits it.
5. Creates the RC tag, for example `apache-parquet-1.18.0-rc0`.
6. Deploys the artifacts to a Nexus staging repository. Then it closes and verifies the repository.
7. Builds and signs the source tarball, and writes its SHA-512 checksum.
8. Stages the tarball, signature, and checksum in
   [dist/dev/parquet](https://dist.apache.org/repos/dist/dev/parquet/).
9. Pushes the RC tag and creates a GitHub pre-release with generated release notes.
10. Writes the VOTE e-mail to the run summary.

Record the **Nexus staging repository ID** from the summary, for example
`orgapacheparquet-1234`.

#### 2\. Review the pre-release notes

Open the [pre-release](https://github.com/apache/parquet-java/releases) that
the workflow created. You can edit the generated notes. For example, remove
unrelated changes (whitespace, test-only changes) and sort the changes to make
them easier to read.

#### 3\. Send the VOTE e-mail to [dev@parquet.apache.org](mailto:dev@parquet.apache.org)

Copy the VOTE e-mail from the run summary. Add a summary of the important
changes in the release. Verify that all of the e-mail text applies to your
release.

### If the vote fails

Run **Release - Cancel RC** with these inputs:

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `version` | Yes | | The release version, for example `1.18.0`. |
| `rc_number` | Yes | | The RC number that failed the vote, for example `0`. |
| `staging_repo_id` | Yes | | The Nexus staging repository ID from the Prepare RC summary, for example `orgapacheparquet-1234`. |
| `allow_description_mismatch` | No | Cleared | Do not verify that the staging repository description is `Apache Parquet <VERSION> RC<NUM>`. Use it only for recovery, when someone changed the description by hand. |
| `dry_run` | No | Selected | Print each command and do not run it. |

Before the workflow drops the staging repository, it verifies that the
repository:

- Belongs to `org.apache.parquet`.
- Is closed.
- Contains the release version.
- Has the expected description.

The workflow drops the Nexus staging repository and removes the RC from
`dist/dev/parquet`. It also writes the vote result e-mail to the run summary.
Add the reason that the vote failed to the e-mail. Then send the e-mail to the
dev list.

The RC tag and the GitHub pre-release stay in place, so no later RC uses the
same RC number. After you fix the issues, run Prepare RC again. It uses the
next RC number.

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
| `allow_description_mismatch` | No | Cleared | Do not verify that the staging repository description is `Apache Parquet <VERSION> RC<NUM>`. Use it only for recovery, when someone changed the description by hand. |
| `dry_run` | No | Selected | Print each command and do not run it. |

Before it changes anything, the workflow verifies that the staging repository:

- Belongs to `org.apache.parquet`.
- Is closed.
- Contains the release version.
- Has the description `Apache Parquet <VERSION> RC<NUM>`.

The workflow also checks out the `parquet-X.Y.x` branch and verifies that the
head of the branch is the RC commit. Then the workflow:

1. Creates the final release tag, for example `apache-parquet-1.18.0`, on the RC commit.
2. Releases the Nexus staging repository to Maven Central.
3. Pushes the release tag and creates the GitHub release.
4. Sets the next development version on the release branch, for example
   `1.18.1-SNAPSHOT`, and pushes it.
5. Writes the remaining manual steps and the ANNOUNCE e-mail to the run summary.

#### 3\. Move the release on dist.apache.org (PMC member)

The run summary has a block of `svn` commands for the release. A PMC member
copies the block and runs it with their own SVN credentials. The commands:

- Move the RC from `dist/dev/parquet` to `dist/release/parquet`.
- Remove the older patch releases of the same minor version that the new
  release replaces. The commands do not change releases of other minor
  versions.

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

Update the downloads page on parquet.apache.org. Add a release blog post. The
run summary has a template for the blog post. The
[contribution page](https://parquet.apache.org/docs/contribution-guidelines/contributing/)
tells you how to update the site.

#### 5\. Send the ANNOUNCE e-mail to [announce@apache.org](mailto:announce@apache.org) and the dev list

Copy the ANNOUNCE e-mail from the run summary. The e-mail links to the
downloads page. Send it after the release is on
[downloads.apache.org](https://downloads.apache.org/parquet/) and after you
update the site.

#### 6\. Update the feature recommendations in parquet-format

Recommendations about when to enable features are usually related to
parquet-java releases. The parquet-format repository has the details. After
each release, update the specification with the recommended date when each new
feature may be enabled.

### Running the release scripts locally

Each workflow runs a script in
[`release/bin`](https://github.com/apache/parquet-java/tree/master/release/bin)
of parquet-java. You can run the scripts on your own machine, for example to
debug a failed run. See the
[release README](https://github.com/apache/parquet-java/blob/master/release/README.md)
for details.

### Release Cadence

If enough volunteers are available, the Parquet community aims to release
every quarter. The target months are January, April, July, and October. If a
new major version is necessary, the community targets the October release for
it.

### Release Verification

The approval process for Apache Parquet releases follows the guidelines on the
Apache Software Foundation [Release Approval](https://www.apache.org/legal/release-policy.html#release-approval) page.

For a release vote to pass, it MUST get a minimum of three positive binding
votes. It MUST also get more positive binding votes than negative binding
votes. No one may veto a release. Votes from PMC members are binding. The
project strongly encourages non-binding votes, which are a sign of a healthy
project.

To cast a vote, you are expected to do the steps that follow.

#### Download the source package, signature, checksum, and KEYS

The release candidate is in `https://dist.apache.org/repos/dist/dev/parquet/`.
The name of the RC folder contains the version and the RC number. For example,
these are the files for Apache Parquet 1.15.0 RC1:

```
wget https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.15.0-rc1/apache-parquet-1.15.0.tar.gz
wget https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.15.0-rc1/apache-parquet-1.15.0.tar.gz.asc
wget https://dist.apache.org/repos/dist/dev/parquet/apache-parquet-1.15.0-rc1/apache-parquet-1.15.0.tar.gz.sha512
wget https://dist.apache.org/repos/dist/release/parquet/KEYS
```

#### Verify the signature and checksum

The project recommends GnuPG. To install it:

- On Linux, run `yum install gnupg` or `apt-get install gnupg`.
- On macOS, run `brew install gnupg`.

```
gpg --import KEYS
gpg --verify apache-parquet-1.15.0.tar.gz.asc apache-parquet-1.15.0.tar.gz
sha512sum --check apache-parquet-1.15.0.tar.gz.sha512
```

#### Verify the license headers

The project recommends Apache RAT to verify the license headers. To download
it, run these commands:

```
wget https://archive.apache.org/dist/creadur/apache-rat-0.16.1/apache-rat-0.16.1-bin.tar.gz
tar zxvf apache-rat-0.16.1-bin.tar.gz
```

Run the command that follows to verify the license headers. The command uses a
regular expression to prevent false positives for some files.

The command prints a summary, a list of the files and their licenses, and each
file that does not have a valid license header.

```
java  -jar apache-rat-0.16.1/apache-rat-0.16.1.jar -a -d apache-parquet-1.15.0.tar.gz -e  "\w+.avsc$|\w+\-2.parquet$|.gitignore|PULL_REQUEST_TEMPLATE.md"
```

#### Verify the build and the tests

See the [building section](https://github.com/apache/parquet-java/blob/master/README.md#building)
of the [parquet-java](https://github.com/apache/parquet-java) README.
