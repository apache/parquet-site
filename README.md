# Parquet Website

This website is built / powered by [Hugo](https://gohugo.io/), and extended from the [Docsy Theme](https://www.docsy.dev/).

The following steps assume that you have `hugo` installed and working.

## Building and Running Locally

Clone this repository to run the website locally:

```shell
git clone git@github.com:apache/parquet-site.git
cd parquet-site
git submodule update --init --recursive
```

To build or update your site’s CSS resources, you also need PostCSS to create the final assets. By default npm installs tools under the directory where you run npm install.

```
npm install -D autoprefixer
npm install -D postcss-cli
npm install -D postcss
```

To run this website site locally, run the following in the root of the directory:

```shell
hugo server
```

# Release Documentation

To create documentation for a new release of `parquet-format` create a new <releaseNumber>.md file under `content/en/blog/parquet-format`. Please see existing files in that directory as an example.

To create documentation for a new release of `parquet-mr` create a new <releaseNumber>.md file under `content/en/blog/parquet-mr`. Please see existing files in that directory as an example.

# Website development and deployment

## Staging
To make a change to the `staging` version of the website:
1. Make a PR against the `staging` branch in the repository
2. Once the PR is merged, the `Build and Deploy Parquet Site`
job in the [deployment workflow](./.github/workflows/deploy.yml) will be run, populating the `asf-staging` branch on this repo with the necessary files.

**Do not directly edit the `asf-staging` branch of this repo**

## Production

To make a change to the `production` version of the website:
1. Make a PR against the `production` branch in the repository
2. Once the PR is merged, the `Build and Deploy Parquet Site`
job in the [deployment workflow](./.github/workflows/deploy.yml) will be run, populating the `asf-site` branch on this repo with the necessary files.

**Do not directly edit the `asf-site` branch of this repo**
