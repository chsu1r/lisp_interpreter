"""6.009 Lab 8A: carlae Interpreter"""

import sys

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '/': lambda args: divide(args),
    '*': lambda args: multiply(args)
}

class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass

class Environment():
    """
    Environment class: contains the variables and the pointer to the parent
    user can define variables and retrieve variables
    """
    def __init__(self,parent = carlae_builtins):
        self.variables = {}
        self.parent_environment = parent
        self.child_environments = []

    def define(self,var,value):
        self.variables[var] = value
    def retrieve(self,variable):
        """
        Retrieving will depend on whether the variable is in this environment
        or the parents.
        :param variable: variable to look up
        :return: the variable value, or if None, raise an error
        """
        k = self.variables.get(variable)
        if k == None:
            if self.parent_environment == None:
                raise EvaluationError
            elif self.parent_environment == carlae_builtins:
                p = carlae_builtins.get(variable)
                if p == None:
                    raise EvaluationError
                return p
            else:
                return self.parent_environment.retrieve(variable)
        return k

class func():
    """
    A class structure to represent functions. Contains the function body (ie the
    series of commands for the function and the variable names.
    """
    def __init__(self,variable_names,body,parent):
        self.vars = variable_names
        self.body = body
        self.env_parent = parent
    def execute(self,variables):
        """
        Execute the function given a list of inputs
        Create an environment to execute code body in
        :param variables: variables to be mapped to the variable names
        :return: evaluate the body with this new function environment
        """
        if len(variables) != len(self.vars):
            raise EvaluationError
        new_env = Environment(parent=self.env_parent)
        for i in range(len(variables)):
            new_env.define(self.vars[i],variables[i])
        k = evaluate(self.body,new_env)
        return k



def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    return_list=[]
    current_word = ''
    ignore = False
    # track character by character, checking if semicolons, spaces, or newlines pop up
    for character in source:
        if ignore and character!='\n':
            continue
        elif ignore and character == '\n':
            ignore = False
        elif character == '(' or character == ')':
            if current_word:
                return_list.append(current_word)
                current_word = ''
            return_list.append(character)
        elif character == ' ' or character == "\n":
            if current_word != '':
                return_list.append(current_word)
            current_word = ''
        elif character == ';':
            ignore = True
            if current_word:
                return_list.append(current_word)
                current_word=''
        else:
            current_word+=character
    if current_word:
        return_list.append(current_word)
    return return_list

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """

    # basically the recursive call for parse to create lists within lists
    def listify(token_list):
        i = 0
        current_list = []
        while token_list:
            if token_list[0]==')':
                token_list = token_list[1:]
                return current_list,token_list
            elif token_list[0]=='(':
                p,token_list = listify(token_list[1:])
                current_list.append(p)
            else:
                if numb(token_list[i]) != False:
                    current_list.append(float(token_list[i]))
                else:
                    current_list.append(token_list[i])
                token_list = token_list[1:]

    # make sure your parantehse are matched
    if not paran_count(tokens):
        raise SyntaxError

    if tokens[0] == '(':
        t = listify(tokens[1:])[0]
        return t
    else:
        if numb(tokens[0]) != False:
            return float(tokens[0])
        else:
            return tokens[0]

# check to see if something can be a float
def numb(k):
    try:
        float(k)
        return float(k)
    except ValueError:
        return False

# check to see if your paranthese are matched
def paran_count(l):
    left = 0
    for token in l:
        if token == '(':
            left += 1
        elif token == ')':
            left -=1
        if left < 0:
            return False
    if left != 0:
        return False
    return True

def divide(l):
    j = l[0]
    for item in l[1:]:
        j = j/item
    return j

def multiply(l):
    j = l[0]
    for item in l[1:]:
        j *= item
    return j


def evaluate(tree,env = Environment()):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    # basically the recursive call for evaluate.
    def recur(current_exp):

        #an empty input
        if current_exp == []:
            raise EvaluationError

        # if youre defining a variable
        if current_exp[0] == "define":

            if type(current_exp[1]) != list:
                f = evaluate(current_exp[2], env)
                env.define(current_exp[1],f)
                return f

            # if youre defining a function lambda
            else:
                p = func(current_exp[1][1:],current_exp[2],Environment(parent=env))
                env.define(current_exp[1][0],p)
                return p

        # if youre trying to do a function
        elif current_exp[0] == "lambda":
            p = func(current_exp[1],current_exp[2],Environment(parent=env))
            return p

        current_function = None

        # if youre trying to retrieve some sort of function
        if type(current_exp[0])!=list:
            current_function = env.retrieve(current_exp[0])
            if current_function == None:
                raise EvaluationError
        # if you have to evaluate the list first
        elif type(current_exp[0]) == list:
            current_function = evaluate(current_exp[0],env)

        # now that you have your function, retrieve ur inputs
        input_values = []
        for value in current_exp[1:]:
            if type(value) != list:
                # if your input is a number
                if type(value) == float or type(value) == int:
                    input_values.append(value)
                # if your input is a variable
                else:
                    v = env.retrieve(value)
                    input_values.append(v)
            # if your input is a list and needs to be eval'd
            else:
                input_values.append(recur(value))
        # now execute ur function (if its a user defined function, otherwise just run it)
        if type(current_function)==func:
            return current_function.execute(input_values)
        return current_function(input_values)

    # if your input isnt a list and you just wanna retrieve a variable or return the tree
    if type(tree) == str:
        v = env.retrieve(tree)
        if v != None:
            return v
    if type(tree) != list:
        return tree
    return recur(tree)

def result_and_env(tree,env=None):
    if env==None:
        env = Environment()
    r = evaluate(tree,env)
    return r,env


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    while True:
        inff = input("in> ")
        if inff == "QUIT":
            break
        k = parse(tokenize(inff))
        print(k)
        print("out> ",evaluate(k))