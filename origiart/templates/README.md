Overview
============
Templates are stored in this `origiart/templates` folder. They are called by views using the `render_template` function. 
These templates all extend the `base.html` template which provides all of the CSS, JS and basic HTML that is common throughout
the application. The basic concept throughout this templating language (known as Jinja2) is to use simple escape sequences to trigger blocks that are processed by the templating engine. For control sequences such as `for` loops or `if` statements, blocks are declared as:
```
{% if foo %}
    <p> awesome html </p>
{% endif %}
```
In order to evaluate/echo a variable inline, you simply wrap the variable name in `{{foo}}`:
```
{% if food %}
    <p> {{foo}} was printed here~ </p>
{% endif %}
```

This base template is broken down into five main blocks, js, css, header, footer and main content.
Each of these can be overridden by child templates to provide more content and or templating.
In this system, pages extend the Base and specify a page name, `{% set PAGENAME = 'Contact'%}`.
More advanced inheritance is used to provide additional functionality such as inheriting a block as well as adding
more content to the block, as will be explained later.

Search Jinja2 templating flask examples for help
