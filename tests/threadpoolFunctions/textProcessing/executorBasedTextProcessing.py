import os
import sys
import unittest
from time import sleep

import logging

from generate_result_report.service.generate_result_report_service_impl import GenerateResultReportServiceImpl
from generate_result_report.service.response.generate_result_report_response import GenerateResultReportResponse
from user_defined_protocol.protocol import UserDefinedProtocolNumber

# 설정
logging.basicConfig(level=logging.INFO)

from generate_result_report.service.request.generate_result_report_request import GenerateResultReportRequest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'template'))

from template.initializer.init_domain import DomainInitializer

from template.request_generator.request_class_map import RequestClassMap
from template.response_generator.response_class_map import ResponseClassMap
from template.custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl

from template.ipc_queue.repository.ipc_queue_repository_impl import IPCQueueRepositoryImpl

from template.thread_worker_pool.service.thread_worker_pool_service_impl import ThreadWorkerPoolServiceImpl
from template.command_executor.service.command_executor_service_impl import CommandExecutorServiceImpl
from template.command_analyzer.repository.command_analyzer_repository_impl import CommandAnalyzerRepositoryImpl


DomainInitializer.initEachDomain()

class TestThreadWorkerPoolService:
    def __init__(self):
        self.ipcQueueRepository = IPCQueueRepositoryImpl.getInstance()
        self.ipcQueueRepository.createEssentialIPCQueue()
        self.ipcAnalyzerExecutorChannel = self.ipcQueueRepository.getIPCAnalyzerExecutorChannel()

        self.custom_request = GenerateResultReportRequest(data=['EDDI-RobotAcademy', 'noodle-backend', 'develop'])
        print(self.custom_request)

        self.customProtocolService = CustomProtocolServiceImpl.getInstance()
        self.generateResultReportService = GenerateResultReportServiceImpl.getInstance()

        requestClassMapInstance = RequestClassMap.getInstance()
        requestClassMapInstance.addRequestClass(
            UserDefinedProtocolNumber.GENERATE_RESULT_REPORT_PROTOCOL_NUMBER,
            GenerateResultReportRequest
        )

        responseClassMapInstance = ResponseClassMap.getInstance()
        responseClassMapInstance.addResponseClass(
            UserDefinedProtocolNumber.GENERATE_RESULT_REPORT_PROTOCOL_NUMBER,
            GenerateResultReportResponse
        )

        self.customProtocolService.registerCustomProtocol(
            UserDefinedProtocolNumber.GENERATE_RESULT_REPORT_PROTOCOL_NUMBER,
            self.generateResultReportService.generateResultReport
        )

        self.threadWorkerPoolService = ThreadWorkerPoolServiceImpl.getInstance()
        self.commandExecutorService = CommandExecutorServiceImpl.getInstance()

        self.commandAnalyzerRepository = CommandAnalyzerRepositoryImpl.getInstance()
        self.commandAnalyzerRepository.injectAnalyzerExecutorChannel(self.ipcAnalyzerExecutorChannel)

        self.commandExecutorService.requestToInjectAnalyzerExecutorChannel(self.ipcAnalyzerExecutorChannel)

        self.threadWorkerPoolService.createThreadWorkerPool("CommandExecutor", 5)
        self.threadWorkerPoolService.allocateExecuteFunction("CommandExecutor", self.commandExecutorService.executeCommand)
        self.threadWorkerPoolService.executeThreadPoolWorker("CommandExecutor")

    def executeThreadPoolWorker(self):
        self.commandAnalyzerRepository.sendDataToCommandExecutor(self.custom_request)

        self.threadWorkerPoolService.shutdownPool("CommandExecutor")

        # results = [future.result() for future in self.futures]
        # expected_results = [f"Command executed by thread {i + 1}" for i in range(5)]
        # self.assertEqual(results, expected_results)

if __name__ == "__main__":
    ttwps = TestThreadWorkerPoolService()
    ttwps.executeThreadPoolWorker()