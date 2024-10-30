from template.request_generator.base_request import BaseRequest
from user_defined_protocol.protocol import UserDefinedProtocolNumber


class ConditionalCustomExecutorMultipleUserTestRequest(BaseRequest):
    def __init__(self, **kwargs):
        self.__protocolNumber = UserDefinedProtocolNumber.CONDITIONAL_CUSTOM_EXECUTOR_MULTIPLE_USER_TEST.value

    def getProtocolNumber(self):
        return self.__protocolNumber

    def toDictionary(self):
        return {
            "protocolNumber": self.__protocolNumber
        }

    def __str__(self):
        return f"ConditionalCustomExecutorMultipleUserTestRequest(protocolNumber={self.__protocolNumber})"