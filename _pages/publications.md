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

<div class="notice--info" style="margin-bottom: 2em; font-size: 2em; text-align: center;">
  <strong style="font-size: 2em" >Total Papers: {{ site.data.pub_stats.total }} </strong>&nbsp;|&nbsp;
  <strong style="font-size: 2em" >First-Author Papers: {{ site.data.pub_stats.first_author }} </strong>&nbsp;|&nbsp;
  <strong style="font-size: 2em" >Selected Contributing Papers:{{ site.data.pub_stats.selected }}</strong> 
  <br>
  <span style="font-size: 2em; font-weight: normal; color: #555;"><i>Click links to read the abstract and key figures.</i></span>
</div>

{% assign first_author_pubs = site.publications | where: "pub_type", "1_first_author" | sort: "date" | reverse %}
{% assign selected_pubs = site.publications | where: "pub_type", "2_selected" | sort: "date" | reverse %}
{% assign other_pubs = site.publications | where: "pub_type", "3_other" | sort: "date" | reverse %}

{% if first_author_pubs.size > 0 %}
<h2>First-Author Publications</h2>
{% for post in first_author_pubs %}
  {% include archive-single.html %}
{% endfor %}
{% endif %}

{% if selected_pubs.size > 0 %}
<h2>Selected Contributing Publications</h2>
{% for post in selected_pubs %}
  {% include archive-single.html %}
{% endfor %}
{% endif %}

{% if other_pubs.size > 0 %}
<h2>Other Contributing Publications</h2>
{% for post in other_pubs %}
  {% include archive-single.html %}
{% endfor %}
{% endif %}
