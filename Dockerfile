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

# Dockerfile for running the Parquet website locally
#
# Build an image called parquet-site with necessary tools
# docker build -t parquet-site .
#
# Run
# run docker container mounting the current directory to /parquet-site and exposing port 1313
# docker run -it -v `pwd`:/parquet-site -p 1313:1313  parquet-site
#
# Now you can run npm and hugo commands in the container
FROM debian:bullseye-slim

# run docker container mounting the current directory to /parquet-site and exposing port 1313

# Install necessary utilities
RUN apt-get update
RUN apt-get install wget git -y xz-utils

# Install extended version of hugo to /hugo
# See releases https://github.com/gohugoio/hugo/releases/tag/v0.124.1
# Note, if on amd64 use https://github.com/gohugoio/hugo/releases/download/v0.124.1/hugo_extended_0.124.1_linux-amd64.tar.gz
RUN wget -O - https://github.com/gohugoio/hugo/releases/download/v0.124.1/hugo_extended_0.124.1_linux-arm64.tar.gz  | tar xz
RUN mv /hugo /usr/local/bin/hugo

# install golang to /go
RUN wget -O - https://go.dev/dl/go1.22.3.linux-amd64.tar.gz | tar xz

# install nodejs to /node-v20.13.1-linux-arm64
RUN wget -O - https://nodejs.org/dist/v20.13.1/node-v20.13.1-linux-arm64.tar.xz | xz -d | tar x

# setup path to find binaries
ENV PATH=/go/bin:/node-v20.13.1-linux-arm64/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin


