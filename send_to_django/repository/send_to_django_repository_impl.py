from send_to_django.repository.send_to_django_repository import SendToDjangoRepository
from template.utility.color_print import ColorPrinter


class SendToDjangoRepositoryImpl(SendToDjangoRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def sendBacklogToDjango(self, ipcExecutorConditionalCustomExecutorChannel, userToken, backlogList):
        ColorPrinter.print_important_message(f"ipcExecutorConditionalCustomExecutorChannel: {ipcExecutorConditionalCustomExecutorChannel}")
        ColorPrinter.print_important_message(f"userToken: {userToken}")
        ColorPrinter.print_important_message(f"backlogList: {backlogList}")
        try:
            ipcExecutorConditionalCustomExecutorChannel.put(
                (
                    12322,
                    {
                        "userToken": userToken,
                        "intermediateData": backlogList,
                        "tag": "/backlog/create"
                    }
                )
            )
        except Exception as e:
            ColorPrinter.print_important_message(f"An error while sending backlog to Django!: {e}")

