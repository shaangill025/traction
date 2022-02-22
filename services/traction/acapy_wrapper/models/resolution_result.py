# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401


class ResolutionResult(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    ResolutionResult - a model defined in OpenAPI

        did_doc: The did_doc of this ResolutionResult.
        metadata: The metadata of this ResolutionResult.
    """

    did_doc: Dict[str, Any]
    metadata: Dict[str, Any]


ResolutionResult.update_forward_refs()