==========
Parameters
==========

:ref:`Scrapy spiders <topics-spiders>` support parameters.

When running a spider, you can pass key-value pairs as arguments for your
spider, either with the ``-a`` command-line switch of the :command:`crawl` or
:command:`runspider` commands, or as keyword arguments for the
:meth:`Crawler.crawl <scrapy.crawler.Crawler.crawl>` method, usually passed
through :meth:`CrawlerProcess.crawl <scrapy.crawler.CrawlerProcess.crawl>` or
:meth:`CrawlerRunner.crawl <scrapy.crawler.CrawlerRunner.crawl>` when
:ref:`using Scrapy as a library <run-from-script>`.

The ``__init__`` method of :class:`Spider <scrapy.spiders.Spider>` receives
those keyword arguments and sets them as spider variables, so that you can
access them from your spider methods.

However, parameter support in Scrapy has some limitations:

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
and then point to it from the ``"params"`` key of a :class:`dict` ``meta``
class variable of your spider:

.. _pydantic.BaseModel: https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel

.. code-block:: python

    from pydantic import BaseModel
    from scrapy import Spider

    class MyParams(BaseModel):
        foo: int

    class MySpider(Spider):
        name = "my_spider"
        meta = {
            "params": MyParams,
        }

To learn how to define parameters in your `pydantic.BaseModel`_
subclass, see the `Pydantic usage documentation
<https://docs.pydantic.dev/latest/usage/models/>`_.

.. _define-params-limits:

However, scrapy-spider-metadata only supports a subset of Pydantic features:

-   Only the following parameter types are supported: :class:`str`,
    :class:`int`, :class:`float`, :class:`bool`, :class:`~enum.Enum`,
    :class:`~enum.IntEnum`.

-   Defining multiple types for a given parameter is not supported.

Using other Pydantic features can prevent scrapy-spider-metadata from working
as expected.

.. note:: If you wish to use a Pydantic feature not listed above, please see if
    it has already been requests in `our issue tracker
    <https://github.com/scrapy-plugins/scrapy-spider-metadata/issues>`_, and if
    not, feel free to request it.


Converting and validating arguments
===================================

Add the :class:`~scrapy_spider_metadata.ParamSpiderMixin` mixin to a spider
with :ref:`defined parameters <define-params>` to make the spider:

-   Halt with an exception if there are missing arguments or any provided
    argument does not match the defined parameter validation rules.

-   Convert arguments to the expected type.

For example, if you modify the :ref:`example above <define-params>` to use the
mixin:

.. code-block:: python
    :emphasize-lines: 3, 8

    from pydantic import BaseModel
    from scrapy import Spider
    from scrapy_spider_metadata import ParamSpiderMixin

    class MyParams(BaseModel):
        foo: int

    class MySpider(ParamSpiderMixin, Spider):
        name = "my_spider"
        meta = {
            "params": MyParams,
        }

And then run the spider with the ``foo`` parameter set to the string ``"42"``,
``self.foo`` in your spider will be the :class:`int` value ``42``, instead of
``"42"``.

Also, if you do not pass a value for ``foo`` at all, the spider will not start,
because ``foo`` is a required parameter. All parameters without a default value
are considered required parameters.

.. autoclass:: scrapy_spider_metadata.ParamSpiderMixin


Getting the parameter specification as JSON Schema
==================================================

Given a spider with :ref:`defined parameters <define-params>`, you can get a
`JSON Schema`_ representation of the parameter specification of that spider
using the :func:`~scrapy_spider_metadata.get_spider_param_schema` function:

.. _JSON Schema: https://json-schema.org/

.. code-block:: pycon

    >>> from scrapy_spider_metadata import get_spider_param_schema
    >>> get_spider_param_schema(MySpider)
    {'properties': {'foo': {'title': 'Foo', 'type': 'integer'}}, 'required': ['foo'], 'title': 'MyParams', 'type': 'object'}

scrapy-spider-metadata uses Pydantic to generate the JSON Schema. However, it
also applies some post-processing to simplify the resulting schema. For
example, the ``$defs`` root key is removed, and :class:`~enum.Enum` metadata is
moved into the corresponding parameter metadata instead.

.. warning:: If you do not follow the :ref:`scrapy-spider-metadata parameter
    definition limitations <define-params-limits>`,
    :func:`~scrapy_spider_metadata.get_spider_param_schema` may return a broken
    or incomplete schema.

.. autofunction:: scrapy_spider_metadata.get_spider_param_schema
