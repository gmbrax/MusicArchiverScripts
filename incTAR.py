import time
import sys
import os
import getopt
import re
import logging
import logging.handlers
from dataclasses import dataclass
import glob
import tarfile

__version__ = '0.0.2'

loggerHandler = logging.handlers.RotatingFileHandler('./runlog.log')
loggerFormatter = logging.Formatter(
    "%(asctime)s:%(module)s:%(levelname)s: %(message)s")
loggerHandler.setFormatter(loggerFormatter)

logger = logging.getLogger('incTAR')
logger.setLevel(20)
logger.addHandler(loggerHandler)


class invalidLoggerSeverity(Exception):
    pass


class emptyOptionsRun(Exception):
    pass


class mutuallyExclusiveOptions(Exception):
    pass


class missingRequiredOption(Exception):
    pass


class invalidRunMode(Exception):
    pass


class workDirectoryNotFound(Exception):
    pass


class invalidFileExtension(Exception):
    pass


class emptyFolder(Exception):
    pass


def addLogRecord(msg, severity):
    try:
        logger.log(severity, msg)
    except:
        addLogRecord("Severidade Inválida no Loggerc", logging.CRITICAL)
        exit(8)


def scriptHeader():
    print(
        f"IncTAR {__version__} \n\nCriador de Backups Incrementais usando TAR "
    )
    print("")
    addLogRecord('Iniciando Script de Backup', logging.INFO)


def scriptUsage():
    print(
        "Uso:\t python3 incTAR.py {-c <filename.tar> {-d <folder location> } | -u <filename.tar>  {-d <folder location}} "
        "[-h] [-v]\n ")
    print(
        'Opções:\n\n-h\t\t\t\t\t\t\tExibe Essa Ajuda\n-c <filename.tar>\t\t\tCria o um novo backup\n-u '
        '<filename.tar>\t\t\tCria um backup incremental apartir do <filename.tar>\n-d <folder location>\t\tEspecifica '
        'o diretório a ser usado\n-v\t\t\t\t\t\t\tAtiva o modo verborrágico\n')


def parseCommandInput():
    @dataclass
    class runModeInfo:
        runMode: str
        runModeArgument: str
        runModeWorkDirectoryFlagPresent: bool
        runModeWorkDirectory: str
        verboseRunMode: bool

    global runData
    runData = runModeInfo(None, None, False, None, False)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:d:u:v")

    except getopt.GetoptError as error:
        print("Erro: Opção não valida ou falta de argumentos")
        print()
        scriptUsage()
        addLogRecord(f"Opção Inválida: {error}", logging.FATAL)
        sys.exit(2)

    try:
        if len(opts) == 0:
            raise emptyOptionsRun

    except emptyOptionsRun:
        print("Erro: Falta de entrada de opções\n")
        scriptUsage()
        addLogRecord("Falta de entrada de opções", logging.FATAL)
        sys.exit(3)

    try:
        for o, a in opts:
            if o == '-v':
                runData.verboseRunMode = True
            elif o == '-h':
                scriptUsage()
                addLogRecord("Imprimindo texto de ajuda e saindo...",
                             logging.INFO)
            elif o == '-c':
                if runData.runMode == 'UPDATE':
                    raise mutuallyExclusiveOptions
                else:
                    runData.runMode = 'CREATE'  # Isso aqui tem virar um constante para se tornar mais facil
                    runData.runModeArgument = a
            elif o == '-u':
                if runData.runMode == 'CREATE':
                    raise mutuallyExclusiveOptions
                else:
                    runData.runMode = 'UPDATE'  # Isso aqui tem virar um constante para se tornar mais facil
                    runData.runModeArgument = a
            elif o == '-d':
                runData.runModeWorkDirectoryFlagPresent = True
                runData.runModeWorkDirectory = a

    except mutuallyExclusiveOptions:
        print("Erro: Opções Mutuamente exclusivas foram inseridas\n")
        scriptUsage()
        addLogRecord("Opções Mutuamente exclusivas foram inseridas",
                     logging.FATAL)
        sys.exit(7)

    try:
        if (runData.runMode == 'CREATE' or runData.runMode == 'UPDATE'):
            if runData.runModeWorkDirectory == None or runData.runModeWorkDirectoryFlagPresent == False:
                raise missingRequiredOption
    except missingRequiredOption:
        print("Erro: Opção Requerida não foi inserida\n")
        scriptUsage()
        addLogRecord("Opção Requerida não foi inserida", logging.FATAL)
        sys.exit(5)


def runScript():
    def runScriptCreateMode(fileList):
        checkFileExists()
        addToTARFile(filesToAdd)

    def runScriptUpdateMode():
        pass

    def printScreenMessageAndLog(message, severity):
        def formatMessage(message):
            if severity == logging.INFO:
                return f"INFO: {message}"
            elif severity == logging.WARNING:
                return f"AVISO: {message}"
            elif severity == logging.ERROR:
                return f"ERRO: {message}"
            elif severity == logging.CRITICAL:
                return f"CRITÍCO: {message}"

        if runData.verboseRunMode == True:
            if severity >= logging.INFO:
                print(formatMessage(message))
                addLogRecord(message, severity)
        else:
            if severity >= logging.WARNING:
                print(formatMessage(message))
            addLogRecord(message, severity)

    def checkWorkDirectoryExistence():
        try:
            if (os.path.exists(runData.runModeWorkDirectory)) == False:
                raise workDirectoryNotFound
        except workDirectoryNotFound:
            printScreenMessageAndLog(
                f"Erro: Diretório {runData.runModeWorkDirectory} não encontrado",
                logging.FATAL)

            exit(50)

    def checkFileExtension():
        try:
            if not bool(re.match(r"\.(tar)", runData.runModeArgument)):
                raise invalidFileExtension
        except invalidFileExtension:
            printScreenMessageAndLog("Formato do arquivo não é válida ", logging.FATAL)
            sys.exit(51)

    def getUserInput(message):
        c = str()
        while c != 'Y' and c != 'N':
            c = input(message + " (Y/N): ")
            c = c.upper()
        if c == 'Y':
            return True
        elif c == 'N':
            return False

    def checkIfDirectoryIsEmpty():
        try:
            if len(os.listdir(runData.runModeWorkDirectory)) == 0:
                raise emptyFolder
            else:
                printScreenMessageAndLog(f"Foram encontrados {len(os.listdir(runData.runModeWorkDirectory))} arquivos",
                                         logging.INFO)
        except emptyFolder:
            printScreenMessageAndLog("Pasta Vazia", logging.FATAL)

            sys.exit(55)

    def getFilesPath():
        return (glob.glob(runData.runModeWorkDirectory + '**/*', recursive=True))

    def checkFileExists():
        if os.path.isfile(runData.runModeArgument):
            printScreenMessageAndLog(f"o arquivo {runData.runModeArgument} já existe", logging.WARNING)
            if not getUserInput("Deseja Proceder Sobrescreevendo o arquivo"):
                printScreenMessageAndLog("Usuário cancelou a operação", logging.WARNING)
                exit(36)

    def addToTARFile(fileList):
        with tarfile.open(runData.runModeArgument, "w") as tar:
            for file in fileList:
                tar.add(file)
                printScreenMessageAndLog(f"Adicionando o arquivo {file} no {runData.runModeArgument}", logging.INFO)

    checkWorkDirectoryExistence()
    checkIfDirectoryIsEmpty()
    #checkFileExtension() # todo: Corrigir essa verificação de extensão de arquivo
    filesToAdd = getFilesPath()

    try:
        if runData.runMode == 'CREATE':
            runScriptCreateMode(filesToAdd)
        elif runData.runMode == 'UPDATE':
            runScriptUpdateMode()
        else:
            raise invalidRunMode
    except invalidRunMode:
        print("Modo de Operação não válida")
        printScreenMessageAndLog("Modo de Operação não válida", logging.FATAL)


if __name__ == '__main__':
    scriptHeader()
    parseCommandInput()
    runScript()
    addLogRecord("Finalizando o Script de Backup", logging.INFO)
