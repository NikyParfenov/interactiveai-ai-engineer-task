HTML_TEMPLATE = """
<title>{{ title }}</title>

<meta name="description" content="{{ meta_description }}">

<h1>{{ headline }}</h1>

<section id="description">
  <p>
    {{ full_description }}
  </p>
</section>

<ul class="key-features">
    {% for feature in key_features %}
    <li>{{ feature }}</li>
    {% endfor %}
</ul>

<section id="neighborhood">
  <p>
    {{ summary }}
  </p>
</section>

<p class="call-to-action">{{ action }}</p>
"""
