<!--
  - Licensed to the Apache Software Foundation (ASF) under one
  - or more contributor license agreements.  See the NOTICE file
  - distributed with this work for additional information
  - regarding copyright ownership.  The ASF licenses this file
  - to you under the Apache License, Version 2.0 (the
  - "License"); you may not use this file except in compliance
  - with the License.  You may obtain a copy of the License at
  -
  -   http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing,
  - software distributed under the License is distributed on an
  - "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  - KIND, either express or implied.  See the License for the
  - specific language governing permissions and limitations
  - under the License.
  -->

# Hugo shortcodes

Shortcodes are Hugo templates called from Markdown content;
see the [Hugo shortcode documentation] for details.

This site uses shortcodes to dynamically generate content from data stored in
the `data/` directory.

For example the [format-versions.html] shortcode is used in the [versions.md]
page to generate the format version tables. The page calls it with Hugo's
shortcode syntax and passes a `table` parameter such as `forward_incompatible`.

[format-versions.html]: format-versions.html
[versions.md]: ../../content/en/docs/File%20Format/versions.md
[Hugo shortcode documentation]: https://gohugo.io/content-management/shortcodes/#custom
