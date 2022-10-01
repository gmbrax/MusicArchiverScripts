import time
import sys
import os
import getopt
from collections import namedtuple

__version__ = '0.0.1'


class invalidOption(Exception):
    pass


class missingArgument(Exception):
    pass


class missingRequiredOption(Exception):
    pass


class positionNotValid(Exception):
    pass


class emptyOptions(Exception):
    pass


class invalidArgument(Exception):
    pass


class optionWithoutArgument(Exception):
    pass


def scriptHeader():
    print(
        f"IncTAR {__version__} \n\nCriador de Backups Incrementais usando TAR "
    )
    print("")


def scriptUsage():
    print(
        "Uso:\t python3 incTAR.py {{-c <filename.tar> -d <folder location> | -u <filename.tar>  -d <folder location}} "
        "[-h]\n "
    )
    print(
        'Opções:\n\n-h\t\t\t\t\t\t\tExibe Essa Ajuda\n-c <filename.tar>\t\t\tCria o um novo backup\n-u '
        '<filename.tar>\t\t\tCria um backup incremental apartir do <filename.tar>\n-d <folder location>\t\tEspecifica '
        'o diretório a ser usado '
    )


def parseArguments():
    pass


def testConditions():
    FIRST_OPTION = 0
    SECOND_OPTION = 2
    option = namedtuple('option', [
        'optionFlag', 'optionPosition', 'optionUseArgument', 'optionHasMutExc',
        'optionMutExc', 'optionHasRequiredOption', 'optionRequiredOption',
        'optionIsOptional'
    ])

    option_c = option('-c', FIRST_OPTION, True, True, ['-u'], True, ['-d'],
                      False)
    option_u = option('-u', FIRST_OPTION, True, True, ['-c'], True, ['-d'],
                      False)
    option_d = option('-d', SECOND_OPTION, True, False, None, False, None,
                      False)
    option_h = option('-h', FIRST_OPTION, False, False, None, False, None,
                      True)
    availableOptions = {
        'c': option_c,
        'u': option_u,
        'd': option_d,
        'h': option_h
    }
    cmdOptions = sys.argv[1:]

    def nonZeroOptions(optionsList):
        return False if len(optionsList) == 0 else True

    def optionChecker():
        index = 0
        print(len(cmdOptions))
        try:
            while index < len(cmdOptions):
                if cmdOptions[index][1:] in list(availableOptions.keys()):
                    if index == availableOptions[cmdOptions[index]
                    [1:]].optionPosition:
                        if availableOptions[cmdOptions[index]
                        [1:]].optionUseArgument:
                            if len(cmdOptions) > index + 1:
                                if cmdOptions[index + 1][1:] not in list(
                                        availableOptions.keys()):
                                    if availableOptions[cmdOptions[index][1:]].optionHasRequiredOption:
                                        if enforceRequiredOptions(index):
                                            index += 2
                                            pass
                                        else:
                                            index += 2
                                    else:
                                        print("Ate aqui tudo ok")
                                        index += 2
                                else:
                                    raise invalidArgument
                            else:
                                raise missingArgument
                        else:
                            if len(cmdOptions) > index + 1:
                                raise optionWithoutArgument
                            else:
                                print("Ate aqui tudo ok")
                                index += 1
                    else:
                        raise invalidOption


        except invalidArgument:
            print("Erro: Argumento inválido")
        except missingArgument:
            print("Erro: Opção requer argumento")
        except optionWithoutArgument:
            print("Opção Não necessita de argumento")
        except positionNotValid:
            print("Posição da opção não é válida")
        except invalidOption:
            print("Opção não é válida")
        except emptyOptions:
            print("E requerido o uso de opções")

    def enforceRequiredOptions(position):
        try:
            if len(cmdOptions) > position + 2:
                if cmdOptions[position + 2] in availableOptions[
                    cmdOptions[position][1:]].optionRequiredOption:
                    print(availableOptions[cmdOptions[position][1:]].optionRequiredOption)
                else:
                    raise missingRequiredOption
            else:
                raise missingRequiredOption
        except missingRequiredOption:
            print("Erro: Opção apresenta necessidade uma opção seguinte")

    try:
        if nonZeroOptions(cmdOptions):
            optionChecker()
        else:
            raise emptyOptions
    except emptyOptions:
        print("Erro: Programa requer opções")


if __name__ == '__main__':
    testConditions()
    # parseArguments()
