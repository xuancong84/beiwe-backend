
comparators = set(["<", ">", "<=", ">=", "==", "!="])

numeric = set(["<",">","<=",">="]) #numerics only accept number values

class BadOperatorError (Exception): pass
class BadLogicError (Exception): pass
    
def tree_parse(logic_entry):
    
    """ structure and vocab:
        
        A logic entry is a single key dictionary, with allowed keys being the logic operators and comparators.
        The value associated with that key depends on the value of the key.
        
        operators (and, or) must have a list of logic entries, e.g. [{logic entry 1}, {logic entry 2}]
        
        comparators (<,>,==,!=) must have a list of 2 values to compare
        
        invert (not) simply has the inner logic entry, eg: {not: {logic entry} }
        """
    operators = logic_entry.keys()
    if len(operators) != 1:
        raise BadLogicError("multiple keys: %s" % operators)
    
    operator = operators[0]
    #any time you see logic_entry[operator] that means we are grabbing the next level in the object
    
    if operator == 'or':
        # print 'or'
        return any( tree_parse(l) for l in logic_entry[operator] )
    
    if operator == 'and':
        # print 'and'
        return all( tree_parse(l) for l in logic_entry[operator] )
    
    if operator == "not":
        # print 'not'
        return not tree_parse(logic_entry[operator])
    
    if operator in comparators:
        # print 'logic!'
        return do_a_logic(logic_entry)
    
    raise BadOperatorError("invalid operator (1): %s" % operator)
    
    
def do_a_logic(logic_entry):
    operator = logic_entry.keys()[0]
    a, b = logic_entry.values()[0]
    # print operator, a, b
    
    if operator in numeric:
        a = float(a)
        b = float(b)
        
    if operator == "<":
        return a < b
    
    if operator == ">":
        return a > b
    
    if operator == "<=" or operator == "=<":
        return a <= b
    
    if operator == ">=" or operator == "=>":
        return a >= b
    
    if operator == "==":
        return a == b
    
    if operator == "!=":
        return a != b

    raise BadOperatorError("invalid operator (2): %s" % operator)


#test basic logic
assert(tree_parse( {"<": [1,2] } ))
assert(not tree_parse( {"<": [2,1] } ))

assert(tree_parse( {">": [2,1] } ))
assert(not tree_parse( {">": [1,2] } ))

assert(tree_parse( {"<=": [1,2] } ))
assert(not tree_parse( {"<=": [2,1] } ))

assert(tree_parse( {"<=": [1,2] } ))
assert(not tree_parse( {"<=": [2,1] } ))

assert(tree_parse( {"==": [1,1] } ))
assert(not tree_parse( {"==": [2,1] } ))

assert(tree_parse( {"!=": [2,1] } ))
assert(not tree_parse( {"!=": [1,1] } ))

#test not
x={"not": {'==': [1,1] }} #false
assert(not tree_parse(x))

x={"not": {'!=': [1,1] }} #true
assert(tree_parse(x))

#test and
x={"and":[
    {'==': [1,1] }, #true
    {'!=': [1,2] }  #true
]} #result should be true
assert( tree_parse(x) )

x={"and":[
    {'==': [1,1] }, #true
    {'!=': [1,1] }  #false
]} #result should be false
assert( not tree_parse(x) )

x={"and":[
    {'==': [1,2] }, #false
    {'!=': [1,2] }  #true
]} #result should be false
assert( not tree_parse(x) )

x={"and":[ #single value
    {'==': [1,1] } #true
]} #result should be true
assert( tree_parse(x) )

x={"and":[ #single value
    {'==': [1,2] } #false
]} #result should be false
assert( not tree_parse(x) )

#test or
x={"or":[
    {'==': [1,1] }, #true
    {'!=': [1,1] }  #false
]} #result should be true
assert( tree_parse(x) )

x={"or":[
    {'==': [1,2] }, #false
    {'!=': [1,2] }  #true
]} #result should be true
assert( tree_parse(x) )

x={"or":[
    {'==': [1,2] }, #false
    {'!=': [1,1] }  #false
]} #result should be false
assert(not tree_parse(x) )

x={"or":[ #single value
    {'==': [1,1] } #true
]} #result should be true
assert( tree_parse(x) )

x={"or":[ #single value
    {'==': [1,2] } #false
]} #result should be false
assert( not tree_parse(x) )
