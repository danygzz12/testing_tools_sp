def compare_returns(expected_output, real_output):
    if real_output is None: 
        return False
    
    # Handle complex numbers separately
    if isinstance(expected_output, complex) or isinstance(real_output, complex):
        return abs(expected_output - real_output) <= 1e-6
    if isinstance(expected_output, float) or isinstance(real_output, float):
        ### compare numbers with a tolerance level
        from math import isclose
        return isclose(expected_output, real_output, rel_tol=1e-6, abs_tol=1e-6)
    if isinstance(expected_output, int) or isinstance(real_output, int):
        return expected_output == real_output
    if isinstance(expected_output, str):
        return expected_output == real_output
    if isinstance(expected_output, dict):
        ### compare the keys: 
        for key in expected_output:
            if key not in real_output:
                return False
        for key in real_output:
            if key not in expected_output:
                return False 
        for key in expected_output:
            if expected_output[key] != real_output[key]:
                return False
        return True
    if isinstance(expected_output, tuple): 
        return expected_output == real_output
    if isinstance(expected_output, list):
        return expected_output == real_output
    return expected_output == real_output



def failed_case_message(expected_output, real_output, func_name, arg, arg_name=True):
    if arg_name:
        arg_text = [str(key)+"="+str(value) for key, value in arg.items()]
    else:
        arg_text = [str(value) for value in arg.values()]
    arg_text = ", ".join(arg_text)
    return f"\nAl llamar {func_name}({arg_text}) el resultado fue: \n{real_output} \nExpected: \n{expected_output} \n"

def grade_code(func):
    import pickle 
    try: 
        with open("testing_tools_sp/tests/tests_" + func.__name__, "rb") as file:
            tests = pickle.load(file)
    except FileNotFoundError:
        return "El nombre de la función es inválido. Vuélvelo a intentar. "
    input_args = tests[1]
    max_score = tests[2]

    try: 
        with open("testing_tools_sp/tests/" + func.__name__, "rb") as file:
            expected_results = pickle.load(file)
    except FileNotFoundError:
        return "El nombre de la función es inválido. Vuélvelo a intentar."
    
    passed_tests = 0
    total_tests = 0
    failed_messages = ""

    for arg, expected_output in zip(input_args, expected_results): 
        total_tests += 1
        real_output = func(**arg)

        passed = compare_returns(expected_output, real_output)

        if passed:
            passed_tests +=1 
            continue 

        failed_messages += failed_case_message(expected_output, real_output, func.__name__, arg)

    score = passed_tests/total_tests*max_score
    feedback = f"Pasaste {passed_tests}/{total_tests}.\nCalificación: {score}"+failed_messages
    return feedback



### For interactive functions: 
from contextlib import redirect_stdout
from io import StringIO
import builtins
import sys

class PatchedInput:
    def __init__(self, input_values):
        self.input_values = input_values
        self.input_copy = input_values.copy()
        self.original_input = builtins.input
        self.original_output = sys.stdout
        self.captured_lines = []
        self.captured_io = StringIO()
        self.input_lines = []
        self.output_lines = []
        self.failed_to_end = False
        self.ended_soon = False
        
    def __enter__(self):
        builtins.input = self.custom_input
        sys.stdout = self.captured_io
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.input_values:
            print("FUNCTION SHOULD HAVE CONTINUED, BUT INSTEAD ENDED.")
            self.ended_soon = True
        builtins.input = self.original_input
        sys.stdout = self.original_output
        self.clean_up()
    
    def custom_input(self, prompt):
        self.input_lines.append(prompt)
        self.captured_lines.append(prompt)
        print(prompt, end='\n')
        if self.input_values:
            return self.input_values.pop(0)
        else:
            print("THE FUNCTION SHOULD HAVE ENDED HERE, BUT INSTEAD CONTINUED.")
            self.failed_to_end = True
            self.__exit__
    
    def clean_up(self):
        self.captured_lines = self.captured_io.getvalue().splitlines()
        if self.failed_to_end:
            self.captured_lines = self.captured_lines[0:self.captured_lines.index("THE FUNCTION SHOULD HAVE ENDED HERE, BUT INSTEAD CONTINUED.")+1]
        i = 0
        for input_line in self.input_lines:
            try:
                self.captured_lines[self.captured_lines.index(input_line)] = input_line + self.input_copy[i]
            except:
                pass
            i += 1

def simulate_interaction(input_values, function, args={}):
    """Function that automatically interacts with an interactive function in Python given a pre-selected
        list of input values. It returns a PatchedInput instance (pi) with pi.captured_lines showing the
        full interaction, pi.failed_to_end =True in case the function did not end with the provided arguments
        and pi.ended_soon=True in case the function ended without using all provided input arguments. 
    
        Parameters:
            input_values (list[str]): The list of pre-selected input values to test the function. 
            function (func): The interactive function which takes the input values. 
            args (dict{str:any}, Optional, default:None): arguments required by the function. 
        
        """
    patched_input = PatchedInput(input_values)
    with patched_input:
        try:
            function(**args)
        except:
            return patched_input
            pass
    return patched_input


def grade_interactive_function(func):
    import pickle 
    try:
        with open("testing_tools_sp/tests/tests_" + func.__name__, "rb") as file:
            test_inputs, args, max_score = pickle.load(file)
    except FileNotFoundError:
        return "El nombre de la función es inválido. Vuélvelo a intentar. "

    try: 
        with open("testing_tools_sp/tests/" + func.__name__, "rb") as file:
            exp_interactions = pickle.load(file)
    except FileNotFoundError:
        return "El nombre de la función es inválido. Vuélvelo a intentar. "
    
    failed_messages = ""

    passed_tests = 0
    total_tests = 0

    for input_values, arg, exp_interaction in zip(test_inputs, args, exp_interactions):
        total_tests += 1
        ### Run the simulation to obtain expected values. 
        real_pi = simulate_interaction(input_values.copy(), func, arg)
        real_interaction = "\n".join(real_pi.captured_lines)

        if exp_interaction != real_interaction:
            failed_messages += failed_case_message(exp_interaction, real_interaction, func.__name__, arg)
        else:
            passed_tests += 1

    score = passed_tests/total_tests*max_score 
    feedback = f"Pasaste {passed_tests}/{total_tests}.\nCalificación: {score}"+failed_messages
    return feedback




