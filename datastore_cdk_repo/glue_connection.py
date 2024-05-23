from constructs import Construct
from aws_cdk import (
    aws_glue_alpha as _glue_alpha,
    
)

class GlueConnection:
    def __init__(self, scope: Construct, id: str, connection_name: str) -> None:
        self.connection = _glue_alpha.Connection.from_connection_name(
                                scope, id,
                                connection_name=connection_name
                            )
        
    def get_connection(self) -> _glue_alpha.IConnection:
        return self.connection
    
    def get_type(self) -> str:
        return self.connection.connection_type.name