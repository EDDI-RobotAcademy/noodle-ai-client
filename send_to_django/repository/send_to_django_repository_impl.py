from send_to_django.repository.send_to_django_repository import SendToDjangoRepository


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

    def sendBacklogToDjango(self, ipcExecutorConditionalCustomExecutorChannel, userToken, backlogList):
        ipcExecutorConditionalCustomExecutorChannel.put(
            (
                30,
                {
                    "userToken": userToken,
                    "intermediateData": backlogList,
                    "tag": "backlog/create"
                }
            )
        )

