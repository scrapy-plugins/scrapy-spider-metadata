===============
Spider metadata
===============

This library allows retrieving spider metadata defined in spider classes.

If a spider class defines :ref:`spider parameters <params>`, their schema will
also be included in the retrieved metadata.

Defining spider metadata
========================

You can declare arbitrary metadata in your spider classes as a dictionary
attribute named ``metadata``:

.. code-block:: python

    from scrapy import Spider

    class MySpider(Spider):
        name = "my_spider"
        metadata = {
            "description": "This is my spider.",
            "category": "My basic spiders",
        }

As this attribute is shared between instances of the class and of its
subclasses, be careful not to modify it in place. Here is a simple way to
add or change some values in a subclass:

.. code-block:: python

    from scrapy import Spider

    class BaseSpider(Spider):
        metadata = {
            "description": "Base spider.",
            "category": "Base spiders",
        }

    class BaseNewsSpider(BaseSpider):
        metadata = {
            **BaseSpider.metadata,
            "description": "Base news spider.",
        }

    class CNNSpider(BaseNewsSpider):
        metadata = {
            **BaseNewsSpider.metadata,
            "description": "CNN spider.",
            "category": "Concrete spiders",
            "website": "CNN",
        }

Getting spider metadata
=======================

scrapy-spider-metadata provides the following function for retrieving the
metadata for a specific spider class:

.. autofunction:: scrapy_spider_metadata.get_spider_metadata
