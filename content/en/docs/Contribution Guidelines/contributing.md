---
title: "Contributing to Parquet-Java"
linkTitle: "Contributing to Parquet-Java"
weight: 3
description: >
  How to contribute to Parquet-Java
---

Pull Requests
-------------

We prefer to receive contributions in the form of GitHub pull requests. Please send pull requests against the [github.com/apache/parquet-java](https://github.com/apache/parquet-java) repository. If you’ve previously forked Parquet from its old location, you will need to add a remote or update your origin remote to [https://github.com/apache/parquet-java.git](https://github.com/apache/parquet-java.git). Here are a few tips to get your contribution in:

1.  Break your work into small, single-purpose patches if possible. It’s much harder to merge in a large change with a lot of disjoint features.
2.  Create an Issue on the [Parquet-Java issues](https://github.com/apache/parquet-java/issues).
3.  Submit the patch as a GitHub pull request against the master branch. For a tutorial, see the GitHub guides on forking a repo and sending a pull request. Prefix your pull request name with the Issue `GH-2935`: (ex: [https://github.com/apache/parquet-java/pull/2951](https://github.com/apache/parquet-java/pull/2951)).
4.  Make sure that your code passes the unit tests. You can run the tests with `mvn test` in the root directory.
5.  Add new unit tests for your code.
6.  All Pull Requests are tested automatically on [GitHub Actions](https://github.com/apache/parquet-java/actions).

If you’d like to report a bug but don’t have time to fix it, you can still [raise an issue](https://github.com/apache/parquet-java/issues), or email the mailing list ([dev@parquet.apache.org](mailto:dev@parquet.apache.org)).

Committers
----------

### Merging a Pull Request

Merging a pull request requires being a committer on the project and approval of the PR by a committer who is not the author.

A pull request can be merged through the GitHub UI. By default, only [squash and merge](https://github.com/apache/parquet-java/blob/824b7d009eb41539cb0e2f73110efc0ac5694251/.asf.yaml#L29) is enabled on the project.

When the PR solves an existing issue, ensure that it references the issue in the Pull-Request template `Closes #1234`. This way the issue is linked to the PR, and GitHub will automatically close the relevant issue when the PR is being merged.

### Semantic versioning

Parquet-Java leverages [semantic versioning](https://semver.org/#semantic-versioning-200) to ensure compatibility for developers and users of the libraries as APIs and implementations evolve. The Maven plugin [`japicmp`](https://github.com/siom79/japicmp) enforces this, and will fail when an API is being changed without going through the correct deprecation cycle. This includes for all the modules, excluding: `parquet-benchmarks`, `parquet-cli`, `parquet-tools`, `parquet-format-structures`, `parquet-hadoop-bundle` and `parquet-pig-bundle`.

All interfaces, classes, and methods targeted for deprecation must include the following:

- `@Deprecated` annotation on the appropriate element
- `@depreceted` javadoc comment including: the version for removal, the appropriate alternative for usage
- Replacement of existing code paths that use the deprecated behavior

```java
/**
 * @param c the current class
 * @return the corresponding logger
 * @deprecated will be removed in 2.0.0; use org.slf4j.LoggerFactory instead.
 */
@Deprecated
public static Log getLog(Class<?> c) {
    return new Log(c);
}
```

Checking for API violations can be done by running `mvn verify -Dmaven.test.skip=true japicmp:cmp`.

### Tracking issues using Milestones

When a PR is raised that fixes a bug, or a feature that you want to target a certain version, make sure to attach a [milestone](https://github.com/apache/parquet-java/milestones). This way other committers can track certain versions, and see what is still pending. For information on the actual release, please check [the release page](releasing.md).

### Maintenance branches

Once a PR has been merged to master, it can be that the commit needs to be backported to maintenance [branches](https://github.com/apache/parquet-java/branches), (ex: [1.14.x](https://github.com/apache/parquet-java/tree/parquet-1.14.x)). The easiest way is to do this locally:

Make sure that the remote is set up correctly:

```sh
git remote add github-apache git@github.com:apache/parquet-java.git
```

Now you can cherry-pick a PR to a previous branch:

```sh
get fetch --all
git checkout parquet-1.14.x
git reset --hard github-apache/parquet-1.14.x
git cherry-pick <hash-from-the-commit>
git push github-apache/parquet-1.14.x
```

Website
-------
### Release Documentation

To create documentation for a new release of `parquet-format` create a new <releaseNumber>.md file under `content/en/blog/parquet-format`. Please see existing files in that directory as an example.

To create documentation for a new release of `parquet-java` create a new <releaseNumber>.md file under `content/en/blog/parquet-java`. Please see existing files in that directory as an example.

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
