from bson import ObjectId

#This triggers NO invalid questions, and is taken from
# https://github.com/onnela-lab/beiwe-backend/wiki/Beiwe-skip-logic-spec#json-spec-for-a-survey-with-skip-logic
VALID_REFERENCE_SURVEY =\
{
 'content': [
  {'answers': [
    {'text': 'Never'},
    {'text': 'Rarely'},
    {'text': 'Occasionally'},
    {'text': 'Frequently'},
    {'text': 'Almost Constantly'}],
   'question_id': '6695d6c4-916b-4225-8688-89b6089a24d1',
   'question_text': 'In the last 7 days, how OFTEN did you EAT BROCCOLI?',
   'question_type': 'radio_button'},
  {'answers': [
    {'text': 'None'},
    {'text': 'Mild'},
    {'text': 'Moderate'},
    {'text': 'Severe'},
    {'text': 'Very Severe'}],
   'display_if': {'>': ['6695d6c4-916b-4225-8688-89b6089a24d1', 0]},
   'question_id': '41d54793-dc4d-48d9-f370-4329a7bc6960',
   'question_text': 'In the last 7 days, what was the SEVERITY of your CRAVING FOR BROCCOLI?',
   'question_type': 'radio_button'},
  {'answers': [
    {'text': 'Not at all'},
    {'text': 'A little bit'},
    {'text': 'Somewhat'},
    {'text': 'Quite a bit'},
    {'text': 'Very much'}],
   'display_if': {'and': [
                          {'>': ['6695d6c4-916b-4225-8688-89b6089a24d1', 0]},
                          {'>': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 0]}
                          ]},
   'question_id': '5cfa06ad-d907-4ba7-a66a-d68ea3c89fba',
   'question_text': 'In the last 7 days, how much did your CRAVING FOR BROCCOLI INTERFERE with your usual or daily activities, (e.g. eating cauliflower)?',
   'question_type': 'radio_button'},
  {'display_if': {'or': [
                         {'and': [
                                  {'<=': ['6695d6c4-916b-4225-8688-89b6089a24d1', 3]},
                                  {'==': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 2]},
                                  {'<': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 3]}
                                 ]},
                         {'and': [
                                  {'<=': ['6695d6c4-916b-4225-8688-89b6089a24d1', 3]},
                                  {'<': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 3]},
                                  {'==': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 2]}
                                 ]},
                         {'and': [
                                  {'==': ['6695d6c4-916b-4225-8688-89b6089a24d1', 4]},
                                  {'<=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 1]},
                                  {'<=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 1]}
                                 ]},
                         ]},
   'question_id': '9d7f737d-ef55-4231-e901-b3b68ca74190',
   'question_text': "While broccoli is a nutritious and healthful food, it's important to recognize that craving too much broccoli can have adverse consequences on your health.  If in a single day you find yourself eating broccoli steamed, stir-fried, and raw with a 'vegetable dip', you may be a broccoli addict.  This is an additional paragraph (following a double newline) warning you about the dangers of broccoli consumption.",
   'question_type': 'info_text_box'},
  {'display_if': {'or': [
                         {'and': [
                                  {'==': ['6695d6c4-916b-4225-8688-89b6089a24d1', 4]},
                                  {'or': [
                                           {'>=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 2]},
                                           {'>=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 2]}
                                          ]}
                                 ]},
                         {'or': [
                                 {'>=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 3]},
                                 {'>=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 3]}
                                ]}
                        ]},
   'question_id': '59f05c45-df67-40ed-a299-8796118ad173',
   'question_text': 'OK, it sounds like your broccoli habit is getting out of hand.  Please call your clinician immediately.',
   'question_type': 'info_text_box'},
  {'question_id': '9745551b-a0f8-4eec-9205-9e0154637513',
   'question_text': 'How many pounds of broccoli per day could a woodchuck chuck if a woodchuck could chuck broccoli?',
   'question_type': 'free_response',
   'text_field_type': 'NUMERIC'},
  {'display_if': {'<': ['9745551b-a0f8-4eec-9205-9e0154637513', 10]},
   'question_id': 'cedef218-e1ec-46d3-d8be-e30cb0b2d3aa',
   'question_text': 'That seems a little low.',
   'question_type': 'info_text_box'},
  {'display_if': {'==': ['9745551b-a0f8-4eec-9205-9e0154637513', 10]},
   'question_id': '64a2a19b-c3d0-4d6e-9c0d-06089fd00424',
   'question_text': 'That sounds about right.',
   'question_type': 'info_text_box'},
  {'display_if': {'>': ['9745551b-a0f8-4eec-9205-9e0154637513', 10]},
   'question_id': '166d74ea-af32-487c-96d6-da8d63cfd368',
   'question_text': "What?! No way- that's way too high!",
   'question_type': 'info_text_box'},
  {'max': '5',
   'min': '1',
   'question_id': '059e2f4a-562a-498e-d5f3-f59a2b2a5a5b',
   'question_text': 'On a scale of 1 (awful) to 5 (delicious) stars, how would you rate your dinner at Chez Broccoli Restaurant?',
   'question_type': 'slider'},
  {'display_if': {'>=': ['059e2f4a-562a-498e-d5f3-f59a2b2a5a5b', 4]},
   'question_id': '6dd9b20b-9dfc-4ec9-cd29-1b82b330b463',
   'question_text': 'Wow, you are a true broccoli fan.',
   'question_type': 'info_text_box'},
  {'question_id': 'ec0173c9-ac8d-449d-d11d-1d8e596b4ec9',
   'question_text': 'THE END. This survey is over.',
   'question_type': 'info_text_box'}],
 'settings': {'number_of_random_questions': None,
  'randomize': False,
  'randomize_with_memory': False,
  'trigger_on_first_download': False},
 'survey_type': 'tracking_survey',
 'timings': [[], [67500], [], [], [], [], []]}


# This triggers every invalid error case.
# yes: Duplicate Question Ids
# yes: NonExistantUUIDReference
# yes: InvalidComparator
# yes: InvalidNumeric
# yes: NumericPointerInvalid
# no: QuestionReferenceOutOfOrder
INVALID_REFERENCE_SURVEY=\
{
 'content': [

  {'answers': [
    {'text': 'None'},
    {'text': 'Mild'},
    {'text': 'Moderate'},
    {'text': 'Severe'},
    {'text': 'Very Severe'}],
   'display_if': {'>': ['6695d6c4-916b-4225-8688-89b6089a24d1', 0]},
   'question_id': '41d54793-dc4d-48d9-f370-4329a7bc6960',
   'question_text': 'In the last 7 days, what was the SEVERITY of your CRAVING FOR BROCCOLI?',
   'question_type': 'checkbox'}, #invalid numeric type reference (was radio button)
    
  {'answers':[ #question out of order (was previously first question)
      {'text':'Never'},
      {'text':'Rarely'},
      {'text':'Occasionally'},
      {'text':'Frequently'},
      {'text':'Almost Constantly'}],
      'question_id':'6695d6c4-916b-4225-8688-89b6089a24d1',
      'question_text':'In the last 7 days, how OFTEN did you EAT BROCCOLI?',
      'question_type':'radio_button'},

  {'answers': [
    {'text': 'Not at all'},
    {'text': 'A little bit'},
    {'text': 'Somewhat'},
    {'text': 'Quite a bit'},
    {'text': 'Very much'}],
   'display_if': {'and': [
                          {'>': ['6695d6c4-916b-4225-8688-89b6089a24d1', 0]},
                          {'>': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 0]}
                          ]},
   'question_id': '5cfa06ad-d907-4ba7-a66a-d68ea3c89fba',
   'question_text': 'In the last 7 days, how much did your CRAVING FOR BROCCOLI INTERFERE with your usual or daily activities, (e.g. eating cauliflower)?',
   'question_type': 'radio_button'},
  {'display_if': {'or': [
                         {'and': [
                                  {'<=': ['6695d6c4-916b-4225-8688-89b6089a24d1', 3]},
                                  {'==': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 2]},
                                  {'<': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 3]}
                                 ]},
                         {'and': [
                                  {'<=': ['6695d6c4-916b-4225-8688-89b6089a24d1', 3]},
                                  {'<': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 3]},
                                  {'==': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 2]}
                                 ]},
                         {'and': [
                                  {'==': ['6695d6c4-916b-4225-8688-89b6089a24d1', 4]},
                                  {'<=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 1]},
                                  {'<=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 1]}
                                 ]},
                         ]},
   'question_id': '9d7f737d-ef55-4231-e901-b3b68ca74190',
   'question_text': "While broccoli is a nutritious and healthful food, it's important to recognize that craving too much broccoli can have adverse consequences on your health.  If in a single day you find yourself eating broccoli steamed, stir-fried, and raw with a 'vegetable dip', you may be a broccoli addict.  This is an additional paragraph (following a double newline) warning you about the dangers of broccoli consumption.",
   'question_type': 'info_text_box'},
  {'display_if': {'or': [
                         {'and': [
                                  {'==': ['6695d6c4-916b-4225-8688-89b6089a24d1', 4]},
                                  {'or': [
                                           {'>=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 2]},
                                           {'>=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 2]}
                                          ]}
                                 ]},
                         {'or': [
                                 {'>=': ['41d54793-dc4d-48d9-f370-4329a7bc6960', 3]},
                                 {'>=': ['5cfa06ad-d907-4ba7-a66a-d68ea3c89fba', 3]}
                                ]}
                        ]},
   'question_id': '59f05c45-df67-40ed-a299-8796118ad173',
   'question_text': 'OK, it sounds like your broccoli habit is getting out of hand.  Please call your clinician immediately.',
   'question_type': 'info_text_box'},
  {'question_id': '9745551b-a0f8-4eec-9205-9e0154637513',
   'question_text': 'How many pounds of broccoli per day could a woodchuck chuck if a woodchuck could chuck broccoli?',
   'question_type': 'free_response',
   'text_field_type': 'SINGLE_LINE_TEXT'}, #invalid numeric pointer reference in a text_field_type
     
  {'display_if': {'<': ['9745551b-a0f8-4eec-9205-9e0154637513', 10]},
   'question_id': 'cedef218-e1ec-46d3-d8be-e30cb0b2d3aa',
   'question_text': 'That seems a little low.',
   'question_type': 'info_text_box'},

  {'display_if': {'<': ['9745551b-a0f8-4eec-9205-9e0154637513', 10]},
   'question_id': 'cedef218-e1ec-46d3-d8be-e30cb0b2d3aa', #this is a duplicate entry with id of the question right before it
   'question_text': 'That seems a little low.',
   'question_type': 'info_text_box'},

  {'display_if':{'<':['BAD_UUID', 10]}, #points to an invalid id
   'question_id':'cedef218-e1ec-46d3-d8be-e30cb0b2d3aa',
   'question_text':'That seems a little low.',
   'question_type':'info_text_box'},
     
  {'display_if': {'===': ['9745551b-a0f8-4eec-9205-9e0154637513 ', 10]}, #invalid comparator
   'question_id': '64a2a19b-c3d0-4d6e-9c0d-06089fd00424',
   'question_text': 'That sounds about right.',
   'question_type': 'info_text_box'},
     
  {'display_if': {'>': ['9745551b-a0f8-4eec-9205-9e0154637513', "this is an invalid numeric entry"]},
   'question_id': '166d74ea-af32-487c-96d6-da8d63cfd368',
   'question_text': "What?! No way- that's way too high!",
   'question_type': 'info_text_box'},
  {'max': '5',
   'min': '1',
   'question_id': '059e2f4a-562a-498e-d5f3-f59a2b2a5a5b',
   'question_text': 'On a scale of 1 (awful) to 5 (delicious) stars, how would you rate your dinner at Chez Broccoli Restaurant?',
   'question_type': 'slider'},
  {'display_if': {'>=': ['059e2f4a-562a-498e-d5f3-f59a2b2a5a5b', 4]},
   'question_id': '6dd9b20b-9dfc-4ec9-cd29-1b82b330b463',
   'question_text': 'Wow, you are a true broccoli fan.',
   'question_type': 'info_text_box'},
  {'question_id': 'ec0173c9-ac8d-449d-d11d-1d8e596b4ec9',
   'question_text': 'THE END. This survey is over.',
   'question_type': 'info_text_box'}],
 'settings': {'number_of_random_questions': None,
  'randomize': False,
  'randomize_with_memory': False,
  'trigger_on_first_download': False},
 'survey_type': 'tracking_survey',
 'timings': [[], [67500], [], [], [], [], []]}