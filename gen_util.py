import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def callee_info(num_back = 1):
     return inspect.getouterframes(inspect.currentframe())[num_back+1]

def print_callee_info(num_back=1):
    print callee_info(num_back)

def callee_name(desc=False):
    if desc:
        print "callee_name:"
    (frame, filename, line_number, \
         function_name, lines, index) =\
            inspect.getouterframes(inspect.currentframe())[2]
    return function_name, line_number


def func_name():
    (frame, filename, line_number, \
         function_name, lines, index) =\
            inspect.getouterframes(inspect.currentframe())[1]
    return function_name

#http://stackoverflow.com/questions/3711184/how-to-use-inspect-to-get-the-callers-info-from-callee-in-python
#(frame, filename, line_number,
#     function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
#    print(frame, filename, line_number, function_name, lines, index)

