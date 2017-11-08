"""6.009 Lab 8A: carlae Interpreter"""

import sys


class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""
    pass


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

def numb(k):
    try:
        float(k)
        return float(k)
    except ValueError:
        return False

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

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '/': lambda args: divide(args),
    '*': lambda args: multiply(args)
}

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


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    def recur(current_exp):
        current_function = carlae_builtins.get(current_exp[0])
        if current_function == None:
            raise EvaluationError
        input_values = []
        for value in current_exp[1:]:
            if type(value) != list:
                input_values.append(value)
            else:
                input_values.append(recur(value))
        return current_function(input_values)
    return recur(tree)


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