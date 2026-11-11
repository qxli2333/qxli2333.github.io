---
layout: archive
title: "Blog"
permalink: /blog/
author_profile: true
---

原创科普与随笔，同步发布于微信公众号。

{% assign articles = site.blog | sort: "title" %}
<ul>
{% for post in articles %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title | markdownify | remove: "<p>" | remove: "</p>" }}</a></li>
{% endfor %}
</ul>
