# -*- coding: utf-8 -*-

import re

ENTITIES_START_ID = 9000

NUM_ID_PATTERN = re.compile(u'^[0-9]*$')
LET_ID_PATTERN = re.compile(u'^[A-Z]*$')
PEOPLE_NAME_PATTERN = re.compile(u'^[A-Z0-9+*". \(\)\/]*$')
ENTITY_NAME_PATTERN = re.compile(u'^[A-Z0-9-+*. \(\)\/]*$')

def parse_register_str(register_str):

  register_str = register_str.replace('\n', ' ')

  tokens = register_str.split(' ')
  tokens = [token for token in tokens if len(token) > 0]

  if len(tokens) < 3:
    raise Exception('Insuficient tokens at register: ' + register_str)
  
  register_id   = get_register_id(tokens)
  register_type = get_register_type(tokens)
  register_name = get_register_name(register_str, register_type, tokens)

  return { 'id' : register_id, 'name' : register_name, 'type': register_type }

def get_register_id(tokens):

  # Get and validate id
  letters_id = tokens[0]
  numbers_id = tokens[1]

  if (not matches(LET_ID_PATTERN, letters_id)) or (len(letters_id) < 2):
    raise Exception('Bad letters id: ' + letters_id)
  
  if not matches(NUM_ID_PATTERN, numbers_id):
    raise Exception('Bad numbers id: ' + numbers_id)
  
  return (int(numbers_id), letters_id)

def get_register_type(register_id):
  if register_id[0] < ENTITIES_START_ID:
    return 'people'
  else:
    return 'entity'
  
def get_register_name(register_str, register_type, tokens):

  # Get name
  index_id = len(tokens[0]) + len(tokens[1]) + 1
  name = register_str[index_id:].strip()

  # Sanitize string
  is_people = (register_type == 'people')

  name = name.replace(',', '.').replace('\x80', '').replace('\x98', '').replace('\x99', '')

  if not is_people:
    name = replace_char_at_index(name, '*', 0)

  if is_people and (not matches(PEOPLE_NAME_PATTERN, name)):
    raise Exception('Invalid name: ' + name)
  
  if (not is_people) and (not matches(ENTITY_NAME_PATTERN, name)):
    print name
    print list(name)
    raise Exception('Invalid name: ' + name)

  return name

def replace_char_at_index(str_val, char, index):
  list_str = list(str_val)
  list_str[index] = char
  return ''.join(list_str)

def matches(pattern, str_val):
  return pattern.match(str_val) != None