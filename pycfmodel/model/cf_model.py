from datetime import date
from typing import Dict, Union, ClassVar, Optional, List, Any, Collection, Type

from pycfmodel.constants import AWS_NOVALUE
from pycfmodel.model.base import CustomModel
from pycfmodel.model.parameter import Parameter
from pycfmodel.model.resources.generic_resource import GenericResource
from pycfmodel.model.resources.resource import Resource
from pycfmodel.model.resources.types import ResourceModels
from pycfmodel.model.types import Resolvable
from pycfmodel.resolver import _extended_bool, resolve


class CFModel(CustomModel):
    AWSTemplateFormatVersion: Optional[date]
    Conditions: Optional[Dict] = {}
    Description: Optional[str] = None
    Mappings: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = {}
    Metadata: Optional[Dict[str, Dict]] = None
    Outputs: Optional[Dict[str, Dict[str, Union[str, Dict]]]] = {}
    Parameters: Optional[Dict[str, Parameter]] = {}
    Resources: Dict[str, Resolvable[Union[ResourceModels, GenericResource]]] = {}
    Rules: Optional[Dict] = {}
    Transform: Optional[List]

    PSEUDO_PARAMETERS: ClassVar[Dict[str, Union[str, List[str]]]] = {
        # default pseudo parameters
        "AWS::AccountId": "123456789012",
        "AWS::NotificationARNs": [],
        "AWS::NoValue": AWS_NOVALUE,
        "AWS::Partition": "aws",
        "AWS::Region": "eu-west-1",
        "AWS::StackId": "",
        "AWS::StackName": "",
        "AWS::URLSuffix": "amazonaws.com",
    }

    def resolve(self, extra_params=None) -> "CFModel":
        extra_params = {} if extra_params is None else extra_params
        # default parameters
        params = {}
        for key, parameter in self.Parameters.items():
            passed_value = extra_params.pop(key, None)
            ref_value = parameter.get_ref_value(passed_value)
            if ref_value is not None:
                params[key] = ref_value

        extended_parameters = {**self.PSEUDO_PARAMETERS, **params, **extra_params}
        dict_value = self.dict()

        if self.Conditions:
            conditions = dict_value.pop("Conditions")
        else:
            conditions = {}
        resolved_conditions = {
            key: _extended_bool(resolve(value, extended_parameters, self.Mappings, {}))
            for key, value in conditions.items()
        }

        resources = dict_value.pop("Resources")
        resolved_resources = {
            key: resolve(value, extended_parameters, self.Mappings, resolved_conditions)
            for key, value in resources.items()
        }
        return CFModel(**dict_value, Conditions=resolved_conditions, Resources=resolved_resources)

    def resources_filtered_by_type(
        self, allowed_types: Collection[Union[str, Type[Resource]]]
    ) -> Dict[str, Dict[str, Resource]]:
        result = {}
        allowed_resource_classes = tuple(x for x in allowed_types if isinstance(x, type))
        for resource_name, resource in self.Resources.items():
            if isinstance(resource, allowed_resource_classes) or resource.Type in allowed_types:
                result[resource_name] = resource
        return result
