---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

<!-- {% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %} -->

{% include base_path %}

<div class="notice--info" style="margin-bottom: 2em; font-size: 1.1em; text-align: center;">
  <strong>Total Papers:</strong> {{ site.data.pub_stats.total }} &nbsp;|&nbsp;
  <strong>First-Author Papers:</strong> {{ site.data.pub_stats.first_author }} &nbsp;|&nbsp;
  <strong>Selected Contributing Papers:</strong> {{ site.data.pub_stats.selected }}
</div>

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
