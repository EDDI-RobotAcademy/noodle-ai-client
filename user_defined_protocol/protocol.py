from enum import Enum


class UserDefinedProtocolNumber(Enum):
    # 예약된 정보 (1, 2, 11, 12, 13, 21) 을 제외하고 사용하도록 함
    GENERATE_BACKLOG_PROTOCOL_NUMBER = 6
    GENERATE_EXAMPLE_BACKLOG_PROTOCOL_NUMBER = 7
    OPENAI_API_TEXT_PROTOCOL_NUMBER = 8

    OPENAI_BACKLOG_PROTOCOL_NUMBER = 30 # 아예 큰 숫자로 부여해서 겹치지 않도록 함
    GENERATE_RESULT_REPORT_PROTOCOL_NUMBER = 31

    USER_TEST_POINT = 12345
    MASSIVE_PACKET_TEST_POINT = 32123
    CONDITIONAL_CUSTOM_EXECUTOR_TEST_POINT = 12321
    CONDITIONAL_CUSTOM_EXECUTOR_INTERMEDIATE_INFO = 12322

    @classmethod
    def hasValue(cls, value):
        return any(value == item.value for item in cls)