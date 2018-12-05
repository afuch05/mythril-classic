from mythril.analysis.ops import *
import logging
from mythril.analysis.report import Issue


class OwnerCheck:
    def __init__(self, is_owner_check=False, owner_comparison=None, constraint=None):
        self.is_owner_check = is_owner_check
        self.owner_comparison = owner_comparison
        self.constraint = constraint


class OwnershipFunction:
    def __init__(self, function_name="", static_address=None, storage_address=None, owner_comparison=None, constraint=None):
        self.function_name = function_name
        self.static_address = static_address
        self.storage_address = storage_address
        self.owner_comparison = owner_comparison
        self.constraint = constraint


def execute(statespace):
    logging.debug("Executing module: OWNERSHIP")

    ''' list with ownership functions '''
    ownership_functions = []

    '''
    function_names_all = set()
    function_names_ownership = set()
    '''

    for k in statespace.nodes:
        node = statespace.nodes[k]
        '''function_names_all.add(node.function_name)'''
        if len(node.constraints) > 0:
            last_constraint = node.constraints[-1]

            owner_check = is_caller_check(last_constraint)
            if owner_check.is_owner_check:
                '''function_names_ownership.add(node.function_name)'''

                ownership_functions.append(
                    OwnershipFunction(
                        node.function_name,
                        get_static_address(owner_check.owner_comparison),
                        get_storage_address(owner_check.owner_comparison),
                        owner_check.owner_comparison,
                        owner_check.constraint,
                    )
                )

    for o in ownership_functions:
        print(o.function_name + ";" + o.static_address + ";" + o.storage_address + ";" + str(o.owner_comparison) + ";" + str(o.constraint))

    '''
    for fn in function_names_all.difference(function_names_ownership):
        print(fn + "; " + str(False))
    '''

    return []


def is_caller_check(constraint) -> OwnerCheck:
    """
    check if the constraint is a NOT(x op y) constraint
    firstly, check if it is a NOT constraint
    then, check if its argument is of type x op y
    """
    if constraint is None:
        return OwnerCheck(False)

    if str(constraint).startswith("Not"):
        arg = constraint.arg(0)
        if isinstance(arg, BoolRef) and arg.num_args() == 2:
            ''' the NOT constraint has one argument that is of type   x op y  '''
            ''' now check if  op  is an equal operator, and either x or y are the caller-address '''
            if arg.decl().name() == "=":
                '''  op  is an equal operator '''
                lhs_is_caller = is_caller_argument(arg.arg(0))
                rhs_is_caller = is_caller_argument(arg.arg(1))

                if lhs_is_caller and not rhs_is_caller:
                    return OwnerCheck(True, arg.arg(1), constraint)
                elif rhs_is_caller and not lhs_is_caller:
                    return OwnerCheck(True, arg.arg(0), constraint)

    ''' TODO: check if constraint is  x != y '''

    return OwnerCheck(False)


def is_caller_argument(arg) -> bool:
    return "caller" in str(arg)


def is_storage_argument(arg) -> bool:
    return "storage" in str(arg)


def get_static_address(arg) -> str:
    strarg = str(arg)
    if "storage" not in strarg:
        return strarg
    return ""


def get_storage_address(arg) -> str:
    strarg = str(arg)
    if "storage" in strarg:
        return strarg
    return ""
