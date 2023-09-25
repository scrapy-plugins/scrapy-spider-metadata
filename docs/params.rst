.. _params:

==========
Parameters
==========

:ref:`Spider arguments <spiderargs>` have some limitations:

-   There is no standard way for spiders to indicate which parameters they
    expect or support.

-   Since arguments can come from the command line, and those are always
    strings, you have to write code to convert arguments to a different type
    when needed.

-   If you want argument validation, such as making sure that arguments are of
    the right type, or that required arguments are present, you must implement
    validation yourself.

scrapy-spider-metadata allows overcoming those limitations.

.. _define-params:

Defining supported parameters
=============================

To define spider parameters, define a subclass of `pydantic.BaseModel`_,
and then make your spider also inherit from
:class:`~scrapy_spider_metadata.Args` with your parameter specification class
as its parameter:

.. _pydantic.BaseModel: https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel

.. code-block:: python

    from pydantic import BaseModel
    from scrapy import Request, Spider
    from scrapy_spider_metadata import Args

    class MyParams(BaseModel):
        pages: int

    class MySpider(Args[MyParams], Spider):
        name = "my_spider"

        def start_requests(self):
            for index in range(1, self.args.pages + 1):
                yield Request(f"https://books.toscrape.com/catalogue/page-{index}.html")


To learn how to define parameters in your `pydantic.BaseModel`_
subclass, see the `Pydantic usage documentation
<https://docs.pydantic.dev/latest/usage/models/>`_.

Defined parameters make your spider:

-   Halt with an exception if there are missing arguments or any provided
    argument does not match the defined parameter validation rules.

-   Expose an instance of your parameter specification class, that contains the
    parsed version of your spider arguments, e.g. converted to their expected
    type.

For example, if you run the spider in the :ref:`example above <define-params>`
with the ``pages`` parameter set to the string ``"42"``, ``self.args.pages`` is
the :class:`int` value ``42`` (``self.pages`` remains ``"42"``).

Also, if you do not pass a value for ``pages`` at all, the spider will not
start, because ``pages`` is a required parameter. All parameters without a
default value are considered required parameters.

.. _params-schema:

Getting the parameter specification as JSON Schema
==================================================

Given a spider class with :ref:`defined parameters <define-params>`, you can
get a `JSON Schema`_ representation of the parameter specification of that
spider using the :func:`~scrapy_spider_metadata.Args.get_param_schema` class
function:

.. _JSON Schema: https://json-schema.org/

.. code-block:: pycon

    >>> MySpider.get_param_schema()
    {'properties': {'pages': {'title': 'Pages', 'type': 'integer'}}, 'required': ['pages'], 'title': 'MyParams', 'type': 'object'}

scrapy-spider-metadata uses Pydantic to generate the JSON Schema, so your
version of pydantic can affect the resulting output.


Parameters API
==============

.. autoclass:: scrapy_spider_metadata.Args
    :members:
