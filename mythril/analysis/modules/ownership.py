from mythril.analysis.ops import *
import logging
from mythril.analysis.report import Issue



class OwnerCheck:
    def __init__(self, is_static=False, is_storage_word=False, constraint=None, caller_value=None, comparison=None):
        self.is_static = is_static
        self.is_storage_word = is_storage_word,
        self.constraint = constraint
        self.caller_value = caller_value
        self.comparison = comparison


def execute(statespace):
    logging.debug("Executing module: OWNERSHIP")

    issues = []

    ''' dictionary: key is the contract-name, value is a list of function names with ownership pattern '''
    ownership_contract_to_functions = dict()
    ownership_function_to_constraint = dict()

    for k in statespace.nodes:
        node = statespace.nodes[k]

        ownership_contract_to_functions.setdefault(node.contract_name, [])

        if len(node.constraints) > 0:
            last_constraint = node.constraints[-1]
            owner_check = is_caller_check(last_constraint)

            if owner_check is not None:
                ownership_contract_to_functions[node.contract_name].append(node.function_name)
                ownership_function_to_constraint[node.function_name] = owner_check.constraint

                '''
                print("contract: " + node.contract_name)
                print("function: " + node.function_name)
                print("caller value: " + str(owner_check.caller_value))
                print("caller comparison: " + str(owner_check.comparison))
                print("is storage word comparison: " + str(owner_check.is_storage_word))
                print("constraint: " + str(owner_check.constraint))

                issues.append(
                    Issue(
                        contract=node.contract_name,
                        function_name=node.function_name,
                        address=None,
                        swc_id=None,
                        title="Ownership",
                        _type="Ownership",
                        description="Found ownership function",
                        bytecode=node.states[-1].environment.code.bytecode,
                        debug=str(owner_check),
                    )
                )
                '''
    print("Ownership functions: " + str(ownership_contract_to_functions))
    print("Function ownership constraint: " + str(ownership_function_to_constraint))

    return issues


def is_caller_check(constraint) -> OwnerCheck:
    """
    check if the constraint is a NOT(x op y) constraint
    firstly, check if it is a NOT constraint
    then, check if its argument is of type x op y
    """
    if constraint is None:
        return None

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
                    return OwnerCheck(False, is_storage_argument(arg.arg(1)), constraint, arg.arg(0), arg.arg(1))
                elif rhs_is_caller and not lhs_is_caller:
                    return OwnerCheck(False, is_storage_argument(arg.arg(0)), constraint, arg.arg(1), arg.arg(0))

    ''' TODO: check if constraint is  x != y '''

    return None


def is_caller_argument(arg) -> bool:
    return "caller" in str(arg)


def is_storage_argument(arg) -> bool:
    return "storage" in str(arg)
