import os
import sys

from generate_backlog.service.generate_backlog_service_impl import GenerateBacklogServiceImpl
from generate_backlog.service.request.generate_backlog_request import GenerateBacklogRequest
from generate_backlog.service.response.generate_backlog_response import GenerateBacklogResponse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'template'))

from template.custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl
from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap

from user_defined_protocol.protocol import UserDefinedProtocolNumber


class UserDefinedProtocolRegister:
    @staticmethod
    def registerGenerateBacklogProtocol():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        generateBacklogService = GenerateBacklogServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.GENERATE_BACKLOG_PROTOCOL_NUMBER,
            GenerateBacklogRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.GENERATE_BACKLOG_PROTOCOL_NUMBER,
            GenerateBacklogResponse
        )

        customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.GENERATE_BACKLOG_PROTOCOL_NUMBER,
            generateBacklogService.generate
        )



    @staticmethod
    def registerUserDefinedProtocol():
        UserDefinedProtocolRegister.registerGenerateBacklogProtocol()

