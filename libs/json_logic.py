import json

from config.constants import (COMPARATORS, NUMERIC_COMPARATORS, NUMERIC_QUESTIONS,
                              FREE_RESPONSE, FREE_RESPONSE_NUMERIC)

class InvalidLogicError(Exception): pass #this is the super class, it should not show up in any validation check

class NonExistantUUIDReference(InvalidLogicError): pass #the uuid referenced does not exist
class InvalidOperator(InvalidLogicError): pass #the comparoter provided is not a valid comparitor
class InvalidNumeric(InvalidLogicError): pass #the value provided (by the admin) to compare against is not numeric
class NumericPointerInvalid(InvalidLogicError): pass #the answer pointed to should be of a numeric answer type but isn't
class QuestionReferenceOutOfOrder(InvalidLogicError): pass #this question references a question that comes after it

#TODO: make an endpoint that returns a dictionary of uuid to any errors that occur
    
def validate_survey_json(json_survey_string):
    return do_validate_survey( json.loads(json_survey_string) )

def validate_survey_from_db(survey):
    return do_validate_survey(survey['content'])

def do_validate_survey(questions):
    errors = { "duplicate_uuids":[] }
    
    #determine duplicate question ids
    question_ids = set()
    for question in questions:
        uuid = question['question_id']
        if question['question_id'] in question_ids:
            errors['duplicate_uuids'].append(uuid)
        question_ids.add(uuid)
        
    #get mapping of uuids to questions...
    questions_dict = {question['question_id']:question for question in questions}
    
    questions_validated = set()
    for question in questions:
        questions_validated.add(question['question_id'])
        try:
            # print question['question_id']
            if "display_if" in question:
                validate_logic_tree(question['display_if'], questions_dict, questions_validated)
            # else:
            #     print question
        except InvalidLogicError as e:
            #the "str(e.__class__).rsplit(".",1)[1][:-2]" below gets string of error type
            errors[question['question_id']] = [str(e.__class__).rsplit(".",1)[1][:-2], str(e)]
    
    return errors


    
def validate_logic_tree(logic_entry, questions_dict, questions_validated):
    """ Structure and vocab:
    A logic entry is a single key dictionary, with allowed keys being the logic operators and comparators.
    The value associated with that key depends on the value of the key.
    
    operators (and, or) must have a list of logic entries, e.g. [{logic entry 1}, {logic entry 2}]
    
    comparators (<,>,==,!=) must have a list of 2 values to compare
    
    invert (not) simply has the inner logic entry, eg: { not: {logic entry} }, and it inverts the output.
    """
    operators = logic_entry.keys()
    if len(operators) != 1:
        raise InvalidOperator(operators)
    
    operator = operators[0]
    # any time you see logic_entry[operator] that means we are grabbing the next level in the object
    
    if operator == 'or' or operator == "and":
        # print 'and/or'
        for l in logic_entry[operator]:
            validate_logic_tree(l, questions_dict, questions_validated)
        return
    
    if operator == "not":
        # print 'not'
        validate_logic_tree(logic_entry[operator], questions_dict, questions_validated)
        return
    
    if operator in COMPARATORS:
        # print 'logic!'
        validate_logic_entry(logic_entry, questions_dict, questions_validated)
        return
    
    raise InvalidOperator(operator)

def validate_logic_entry(logic_entry, questions_dict, questions_validated):
    comparator = logic_entry.keys()[0]
    uuid, comparator_value = logic_entry.values()[0]
    
    if uuid not in questions_dict:
        raise NonExistantUUIDReference(uuid)
    
    if uuid not in questions_validated:
        raise QuestionReferenceOutOfOrder(uuid)
    
    if comparator in NUMERIC_COMPARATORS:
        try:
            float(comparator_value)
        except ValueError:
            raise InvalidNumeric(comparator_value)
    
    question_type = questions_dict[uuid]['question_type']
    if (question_type not in NUMERIC_QUESTIONS
        or (question_type == FREE_RESPONSE and questions_dict[uuid][
            "text_field_type"] != FREE_RESPONSE_NUMERIC)):
        raise NumericPointerInvalid(uuid)
        
###############################################################################################
##########  THIS IS NEVER GOING TO BE PRODUCTION CODE, IT IS FOR REFERENCE ONLY. ##############
###############################################################################################
#
# class BadOperatorError (Exception): pass
# class BadLogicError (Exception): pass
#
# def logic_tree_parse(logic_entry):
#     """ Structure and vocab:
#         A logic entry is a single key dictionary, with allowed keys being the logic operators and comparators.
#         The value associated with that key depends on the value of the key.
#
#         operators (and, or) must have a list of logic entries, e.g. [{logic entry 1}, {logic entry 2}]
#
#         comparators (<,>,==,!=) must have a list of 2 values to compare
#
#         invert (not) simply has the inner logic entry, eg: { not: {logic entry} }, and it inverts the output.
#         """
#     operators = logic_entry.keys()
#     if len(operators) != 1:
#         raise BadLogicError("multiple keys: %s" % operators)
#
#     operator = operators[0]
#     #any time you see logic_entry[operator] that means we are grabbing the next level in the object
#
#     if operator == 'or':
#         # print 'or'
#         return any(logic_tree_parse(l) for l in logic_entry[operator])
#
#     if operator == 'and':
#         # print 'and'
#         return all(logic_tree_parse(l) for l in logic_entry[operator])
#
#     if operator == "not":
#         # print 'not'
#         return not logic_tree_parse(logic_entry[operator])
#
#     if operator in COMPARATORS:
#         # print 'logic!'
#         return do_logic(logic_entry)
#
#     raise InvalidComparator(operator)
#
#
# def do_logic(logic_entry):
#
#     comparator = logic_entry.keys()[0]
#     a, b = logic_entry.values()[0]
#     # print operator, a, b
#     #FIXME: this float(a) is always a uuid value
#     if comparator in NUMERIC_COMPARATORS:
#         a = float(a)
#         b = float(b)
#
#     if comparator == "<":
#         return a < b
#
#     if comparator == ">":
#         return a > b
#
#     if comparator == "<=":
#         return a <= b
#
#     if comparator == ">=":
#         return a >= b
#
#     if comparator == "==":
#         return a == b
#
#     if comparator == "!=":
#         return a != b
#
#     raise BadOperatorError("invalid operator (2): %s" % comparator)
#
# assert(logic_tree_parse({"<": [1, 2]}))
# assert(not logic_tree_parse({"<": [2, 1]}))
#
# assert(logic_tree_parse({">": [2, 1]}))
# assert(not logic_tree_parse({">": [1, 2]}))
#
# assert(logic_tree_parse({"<=": [1, 2]}))
# assert(not logic_tree_parse({"<=": [2, 1]}))
#
# assert(logic_tree_parse({"<=": [1, 2]}))
# assert(not logic_tree_parse({"<=": [2, 1]}))
#
# assert(logic_tree_parse({"==": [1, 1]}))
# assert(not logic_tree_parse({"==": [2, 1]}))
#
# assert(logic_tree_parse({"!=": [2, 1]}))
# assert(not logic_tree_parse({"!=": [1, 1]}))
#
# #test not
# x={"not": {'==': [1,1] }} #false
# assert(not logic_tree_parse(x))
#
# x={"not": {'!=': [1,1] }} #true
# assert(logic_tree_parse(x))
#
# #test and
# x={"and":[
#     {'==': [1,1] }, #true
#     {'!=': [1,2] }  #true
# ]} #result should be true
# assert(logic_tree_parse(x))
#
# x={"and":[
#     {'==': [1,1] }, #true
#     {'!=': [1,1] }  #false
# ]} #result should be false
# assert(not logic_tree_parse(x))
#
# x={"and":[
#     {'==': [1,2] }, #false
#     {'!=': [1,2] }  #true
# ]} #result should be false
# assert(not logic_tree_parse(x))
#
# x={"and":[ #single value
#     {'==': [1,1] } #true
# ]} #result should be true
# assert(logic_tree_parse(x))
#
# x={"and":[ #single value
#     {'==': [1,2] } #false
# ]} #result should be false
# assert(not logic_tree_parse(x))
#
# #test or
# x={"or":[
#     {'==': [1,1] }, #true
#     {'!=': [1,1] }  #false
# ]} #result should be true
# assert(logic_tree_parse(x))
#
# x={"or":[
#     {'==': [1,2] }, #false
#     {'!=': [1,2] }  #true
# ]} #result should be true
# assert(logic_tree_parse(x))
#
# x={"or":[
#     {'==': [1,2] }, #false
#     {'!=': [1,1] }  #false
# ]} #result should be false
# assert(not logic_tree_parse(x))
#
# x={"or":[ #single value
#     {'==': [1,1] } #true
# ]} #result should be true
# assert(logic_tree_parse(x))
#
# x={"or":[ #single value
#     {'==': [1,2] } #false
# ]} #result should be false
# assert(not logic_tree_parse(x))