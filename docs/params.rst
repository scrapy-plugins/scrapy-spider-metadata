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
    from scrapy_spider_metadata import Args

    class MyParams(BaseModel):
        foo: int

    class MySpider(Args[MyParams], Spider):
        name = "my_spider"

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

Defined parameters make your spider:

-   Halt with an exception if there are missing arguments or any provided
    argument does not match the defined parameter validation rules.

-   Expose an instance of your parameter specification class, that contains the
    parsed version of your spider arguments, e.g. converted to their expected
    type.

For example, if you run the spider in the :ref:`example above <define-params>`
with the ``foo`` parameter set to the string ``"42"``, ``self.args.foo`` is the
:class:`int` value ``42`` (``self.foo`` remains ``"42"``).

Also, if you do not pass a value for ``foo`` at all, the spider will not start,
because ``foo`` is a required parameter. All parameters without a default value
are considered required parameters.


Getting the parameter specification as JSON Schema
==================================================

Given a spider class with :ref:`defined parameters <define-params>`, you can
get a `JSON Schema`_ representation of the parameter specification of that
spider using the :func:`~scrapy_spider_metadata.Args.get_param_schema` class
function:

.. _JSON Schema: https://json-schema.org/

.. code-block:: pycon

    >>> MySpider.get_param_schema()
    {'properties': {'foo': {'title': 'Foo', 'type': 'integer'}}, 'required': ['foo'], 'title': 'MyParams', 'type': 'object'}

scrapy-spider-metadata uses Pydantic to generate the JSON Schema. However, it
also applies some post-processing to simplify the resulting schema. For
example, the ``$defs`` root key is removed, and :class:`~enum.Enum` metadata is
moved into the corresponding parameter metadata instead.

.. warning:: If you do not follow the :ref:`scrapy-spider-metadata parameter
    definition limitations <define-params-limits>`,
    :func:`~scrapy_spider_metadata.get_spider_param_schema` may return a broken
    or incomplete schema.


Parameters API
==============

.. autoclass:: scrapy_spider_metadata.Args
    :members:
