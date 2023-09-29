from typing import Any, Dict, Generic, TypeVar

from pydantic import BaseModel

from ._utils import get_generic_param, normalize_param_schema

ParamSpecT = TypeVar("ParamSpecT", bound=BaseModel)


class Args(Generic[ParamSpecT]):
    """Validates and type-converts :ref:`spider arguments <spiderargs>` into
    the :attr:`args` instance attribute according to the :ref:`spider parameter
    specification <define-params>`.
    """

    def __init__(self, *args, **kwargs) -> None:
        param_model = get_generic_param(self.__class__, Args)
        #: :ref:`Spider arguments <spiderargs>` parsed according to the
        #: :ref:`spider parameter specification <define-params>`.
        assert param_model is not None
        self.args: ParamSpecT = param_model(**kwargs)
        super().__init__(*args, **kwargs)

    @classmethod
    def get_param_schema(cls, normalize: bool = False) -> Dict[Any, Any]:
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
