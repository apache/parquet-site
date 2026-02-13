# Parquet Website

This repository contains the source code for https://parquet.apache.org/

This website is built / powered by [Hugo](https://gohugo.io/) with the [Docsy Theme](https://www.docsy.dev/).

The following steps assume that you have `hugo` installed and working.
You can also use docker, see the [Docker section](#docker) for more information.

## Updating `/docs/file-format` documentation

The `/docs/file-format` pages (for example, https://parquet.apache.org/docs/file-format/data-pages/encodings/) are automatically 
generated from the `parquet-format` repository. 
To update the website to reflect the latest documentation, you need to update the 
submodule in this repository. 


```shell
cd assets/parquet-format
git checkout master
git pull # update to the latest version of parquet-format
cd ../..
git add assets/parquet-format
git commit -m "Update parquet-format submodule"
git push
```


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

To preview this website locally, run the following in the root of the directory:

```shell
hugo server
```

### Building metadata diagrams

To build the metadata svg diagrams, you need mermaid.js installed. You can install it using npm:

```
npm install -D @mermaid-js/mermaid-cli
```

Then you can build the diagrams using the following command:

```
cd static/images
npx mmdc -i FileMetaData.mermaid -o FileMetaData.svg
npx mmdc -i PageHeader.mermaid -o PageHeader.svg
```

## Building and Running in Docker

If you don't want to install `hugo` and its dependencies on your local machine,
you can use docker. To do so, checkout the `parquet-site` repo as explained
above and then use [Dockerfile](Dockerfile) to build an image with the required
tools:

```shell
docker build -t parquet-site .
```

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

# Docsy Templates

The HTML for this site comes from the Docsy theme templates, located in the
`github.com/google/docsy` module, which is a dependency of this project.
Overrides to the default Docsy templates are in the `layouts/` directory. For
example, `layouts/partials/` contains the partial templates for HTML pages.

To make a change to the Docsy templates, copy the template you want to change
from the Docsy module to the `layouts/` directory and then make your changes
there. You can compare the contents of `layouts` with the Docsy templates to see
what has been overridden. For example, to see the difference between the default
Docsy navbar , use a command such as:

```shell
diff -du ~/go/pkg/mod/github.com/google/docsy@v0.12.0/layouts/_partials/navbar.html layouts/partials/navbar.html
```

This compares the local copy with the Docsy theme template in the local Go cache,
in this case `~/go/pkg/mod/github.com/google/docsy@v0.12.0/`.

# parquet-java Release Announcement Process

To create documentation for a new release of `parquet-format` create a new <releaseNumber>.md file under `content/en/blog/parquet-format`. Please see existing files in that directory as an example.

To create documentation for a new release of `parquet-java` create a new <releaseNumber>.md file under `content/en/blog/parquet-java`. Please see existing files in that directory as an example.

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
