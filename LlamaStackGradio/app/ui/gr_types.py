from typing import TypedDict
from typing_extensions import Literal

class Response(TypedDict):
    status: Literal['success', 'error']
    content: any
    markdown: str

class GRDocument(TypedDict):
    file: str
    file_extension: str
    content: str
    path: str