from logging import getLogger
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from pydantic import BaseModel, ValidationError

from ._utils import get_generic_param, normalize_param_schema
from .defaults import FromSetting

if TYPE_CHECKING:
    from scrapy.crawler import Crawler

ParamSpecT = TypeVar("ParamSpecT", bound=BaseModel)
logger = getLogger(__name__)


class Args(Generic[ParamSpecT]):
    """Validates and type-converts :ref:`spider arguments <spiderargs>` into
    the :attr:`args` instance attribute according to the :ref:`spider parameter
    specification <define-params>`.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        param_model = get_generic_param(self.__class__, Args)
        #: :ref:`Spider arguments <spiderargs>` parsed according to the
        #: :ref:`spider parameter specification <define-params>`.
        assert param_model is not None
        try:
            self.args: ParamSpecT = param_model(**kwargs)
        except ValidationError as e:
            # Log the message explicitly, when using the “scrapy crawl” command
            # the exception seems to be silenced somehow instead of showing up
            # in the command output otherwise.
            logger.error(f"Spider parameter validation failed: {e}")
            raise
        super().__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler: "Crawler", *args: Any, **kwargs: Any) -> "Args[ParamSpecT]":
        spider = cast("Args[ParamSpecT]", cast("Any", super()).from_crawler(crawler, *args, **kwargs))

        if not hasattr(spider, "args") or spider.args is None:
            return spider

        param_model = get_generic_param(cls, Args)
        assert param_model is not None
        assert issubclass(param_model, BaseModel)

        # compat Pydantic v1/v2
        if hasattr(spider.args, "model_dump"):
            data = spider.args.model_dump(exclude_unset=True)
        else:
            data = spider.args.dict(exclude_unset=True)

        fields = getattr(param_model, "model_fields", None) or getattr(
            param_model, "__fields__", {}
        )

        for field_name, field in fields.items():
            default_val = getattr(field, "default", None)
            if field_name in data and data[field_name] is not None:
                continue
            if isinstance(default_val, FromSetting):
                getter_name = default_val.getter or "get"
                getter = getattr(crawler.settings, getter_name, crawler.settings.get)
                value = getter(default_val.name, default_val.default)
                if value is not None:
                    data[field_name] = value

        try:
            spider.args = cast("ParamSpecT", param_model(**data))
        except ValidationError as e:
            logger.error(f"Spider parameter validation failed: {e}")
            raise

        return spider

    @classmethod
    def get_param_schema(cls, normalize: bool = False) -> dict[Any, Any]:
        """Return a :class:`dict` with the :ref:`parameter definition
        <define-params>` as `JSON Schema`_.

        .. _JSON Schema: https://json-schema.org/

        If *normalize* is ``True``, the returned schema will be the same
        regardless of whether you are using Pydantic 1.x or Pydantic 2.x. The
        normalized schema may not match the output of any Pydantic version, but
        it will be functionally equivalent where possible.
        """
        param_model = get_generic_param(cls, Args)
        assert param_model is not None
        assert issubclass(param_model, BaseModel)
        try:
            param_schema = param_model.model_json_schema()
        except AttributeError:  # pydantic 1.x
            param_schema = param_model.schema()
        if normalize:
            normalize_param_schema(param_schema)
        return param_schema
