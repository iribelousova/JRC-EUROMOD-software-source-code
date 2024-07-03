API Reference
=============

This reference documentation details the public objects of the Euromod Connector package. For a complete documentation please refer to the Euromod Connector User Guide. 
For futher readings on the tax-benefit microsimulation model EUROMOD please visit the official `web-site <https://euromod-web.jrc.ec.europa.eu/>`_.  [#f1]_

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

.. [#f1] Created with `Euromod web-site <https://euromod-web.jrc.ec.europa.eu/>`_
