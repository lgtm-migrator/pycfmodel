"""
Copyright 2018-2020 Skyscanner Ltd

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import ClassVar, List, Optional

from .iam_managed_policy import IAMManagedPolicy
from ..base import CustomModel
from ..types import ResolvableStr, Resolvable
from .resource import Resource
from .iam_policy import IAMPolicy
from ...constants import REGEX_AWS_MANAGED_ARN


class IAMGroupProperties(CustomModel):
    GroupName: Optional[ResolvableStr] = None
    ManagedPolicyArns: Optional[Resolvable[List[ResolvableStr]]] = None
    Path: Optional[ResolvableStr] = None
    Policies: Optional[Resolvable[List[IAMPolicy]]] = None

    @property
    def ManagedPolicies(self) -> List[IAMManagedPolicy]:
        return [
            IAMManagedPolicy.from_arn(managed_policy_arn)
            for managed_policy_arn in self.ManagedPolicyArns
            if REGEX_AWS_MANAGED_ARN.match(managed_policy_arn)
        ]


class IAMGroup(Resource):
    TYPE_VALUE: ClassVar = "AWS::IAM::Group"
    Type: str = TYPE_VALUE
    Properties: Resolvable[IAMGroupProperties]
