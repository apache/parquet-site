# Apache Parquet Website

This is the website for Apache Parquet. 

### Development Setup
We use middleman to generate the website content from markdown and other 
dynamic templates. The following steps assume you have a working 
ruby environment setup

	gem install bundler
	bundle install

### Generating the website
---
To generate the static wesbite for Apache Parquet run the following commands

		bundle exec middleman build


### Live Development 
---
Live development of the site enables automatic reload when changes are saved. 
To enable run the following command and then open a browser and navigate to 
[http://localhost:4567](http://localhost:4567/) 

		bundle exec middleman 


### Publishing the Site
The website uses svnpubsub. The publish folder contains the websites content
and when committed to the svn repository it will be automatically deployed to 
the live site. 


### Apache License
---
Except as otherwise noted this software is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
