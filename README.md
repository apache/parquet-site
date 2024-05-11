# Parquet Website

This website is built / powered by [Hugo](https://gohugo.io/), and extended from the [Docsy Theme](https://www.docsy.dev/).

The following steps assume that you have `hugo` installed and working. 
You can also use docker, see the [Docker section](#docker) for more information.

## Building and Running Locally

Clone this repository to run the website locally:

```shell
git clone git@github.com:apache/parquet-site.git
cd parquet-site
git submodule update --init --recursive
```

To build or update CSS resources, you also need PostCSS to create the final assets.  By default npm installs tools under the directory where you run npm install.

```
npm install -D autoprefixer
npm install -D postcss-cli
npm install -D postcss
```

To preview this website site locally, run the following in the root of the directory:

```shell
hugo server
```

## Building and Running in Docker

If you don't want to install `hugo` and its dependencies on your local machine,
you can use docker. To do so, checkout the `parquet-site` repo as explained
above and then use [Dockerfile](Dockerfile) to build an image with the required
tools:

```shell
docker build -t parquet-site .
````

Then run the container mounting the current directory to `/parquet-site` and
exposing local port 1313:

```shell
docker run -it -v `pwd`:/parquet-site -p 1313:1313  parquet-site
```

Once inside the container, run the following to preview the site:
```shell
# Install necessary npm modules in parquet-site directory
cd parquet-site
npm install -D autoprefixer
npm install -D postcss-cli
npm install -D postcss
hugo server --bind 0.0.0.0 # run the server
```

You can now preview the site locally on http://localhost:1313/

# Release Process

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
