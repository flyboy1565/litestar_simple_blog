from typing import Annotated
from dataclasses import dataclass

from litestar.params import Parameter


@dataclass
class UserForm:
    username: Annotated[str, Parameter(query="username")]
    first_name: Annotated[str, Parameter(query="first name")]
    last_name: Annotated[str, Parameter(query="last name")]
