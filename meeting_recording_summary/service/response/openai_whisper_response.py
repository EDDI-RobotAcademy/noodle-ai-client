from user_defined_protocol.protocol import UserDefinedProtocolNumber


class OpenAIWhisperResponse:
    def __init__(self, responseData):
        self.protocolNumber = UserDefinedProtocolNumber.OPENAI_WHISPER_PROTOCOL_NUMBER.value

        for key, value in responseData.items():
            setattr(self, key, value)

    @classmethod
    def fromResponse(cls, responseData):
        return cls(responseData)

    def toDictionary(self):
        return self.__dict__

    def __str__(self):
        return f"OpenAIWhisperResponse({self.__dict__})"