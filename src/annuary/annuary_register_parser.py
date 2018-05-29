# -*- coding: utf-8 -*-

import re

COMMUNITY_START_ID = 9000
MAX_NUM_ID = 9850

NUM_ID_PATTERN = re.compile(u'^[0-9]*$')
LET_ID_PATTERN = re.compile(u'^[A-Z]*$')
PERSON_NAME_PATTERN = re.compile(u'^[A-Z0-9+*". \(\)\/]*$')
COMMUNITY_NAME_PATTERN = re.compile(u'^[A-Z0-9-+*. \(\)\/]*$')
PARENTHESIS_GROUP = re.compile(u'\(([A-Za-z0-9]+)\)')
NUMBERS_GROUP = re.compile(u'\d+')

class AnnuaryParsingException(Exception):

  INSUFICIENT_TOKENS = 1
  BAD_LETTER_ID = 2
  BAD_NUMERIC_ID = 3
  ID_OUT_OF_RANGE = 4
  IVALID_NAME = 5

  def __init__(self, message, code):
    Exception.__init__(self, message)
    self.error_code = code

def parse_annuary_register_str(register_str):

  # Make a single line and tokenize
  register_str = register_str.replace('\n', ' ')
  tokens = tokenize(register_str)

  if len(tokens) < 3:
    msg = 'Insuficient tokens at register: ' + register_str
    raise AnnuaryParsingException(msg, AnnuaryParsingException.INSUFICIENT_TOKENS)

  # Get fields
  register_id   = get_register_id(tokens)
  register_type = get_register_type(register_id)
  register_name = get_register_name(register_str, register_type, tokens)
  register_info = get_register_info(register_name, register_type)

  for info in register_info:
    register_name = register_name.replace(info, '').strip()

  return {
    'num_id'  : register_id[0],
    'text_id' : register_id[1],
    'name'    : register_name,
    'type'    : register_type,
    'info'    : ' '.join(register_info).strip()
  }

def parse_num_id_only(register_str):

  # Make a single line and tokenize
  register_str = register_str.replace('\n', ' ')
  tokens = tokenize(register_str)

  if len(tokens) < 3:
    msg = 'Insuficient tokens at register: ' + register_str
    raise AnnuaryParsingException(msg, AnnuaryParsingException.INSUFICIENT_TOKENS)
  
  return get_register_number_id(tokens)

def get_register_id(tokens):

  # Get and validate id
  letters_id = get_register_letters_id(tokens)
  numbers_id = get_register_number_id(tokens)
  
  return (numbers_id, letters_id)

def get_register_letters_id(tokens):
  letters_id = tokens[0]

  # Validate
  if (not matches(LET_ID_PATTERN, letters_id)) or (len(letters_id) < 2):
    msg = 'Bad letters id: ' + letters_id
    raise AnnuaryParsingException(msg, AnnuaryParsingException.BAD_LETTER_ID)
  
  return letters_id

def get_register_number_id(tokens):
  numbers_id = tokens[1]

  # Validate
  if not matches(NUM_ID_PATTERN, numbers_id):
    msg = 'Bad numbers id: ' + numbers_id
    raise AnnuaryParsingException(msg, AnnuaryParsingException.BAD_NUMERIC_ID)

  if int(numbers_id) > MAX_NUM_ID:
    msg = 'Numbers id out of range: ' + numbers_id
    raise AnnuaryParsingException(msg, AnnuaryParsingException.ID_OUT_OF_RANGE)
  
  return int(numbers_id)

def get_register_type(register_id):
  if register_id[0] < COMMUNITY_START_ID:
    return 'person'
  else:
    return 'community'
  
def get_register_name(register_str, register_type, tokens):

  # Get name
  index_id = len(tokens[0]) + len(tokens[1]) + 1
  name = register_str[index_id:].strip()

  # Sanitize name
  name = name.replace(',', '.').replace('\x80', '').replace('\x98', '').replace('\x99', '')

  is_person = (register_type == 'person')
  if not is_person:
    name = replace_char_at_index(name, '*', 0)

  # Validate name
  if is_person and (not matches(PERSON_NAME_PATTERN, name)):
    msg = 'Invalid name: ' + name
    raise AnnuaryParsingException(msg, AnnuaryParsingException.IVALID_NAME)
  
  if (not is_person) and (not matches(COMMUNITY_NAME_PATTERN, name)):
    msg = 'Invalid name: ' + name
    raise AnnuaryParsingException(msg, AnnuaryParsingException.IVALID_NAME)

  return name

def get_register_info(register_name, register_type):

  info = []

  # Things in parenthesis is info
  in_parenthesis = PARENTHESIS_GROUP.search(register_name)
  if in_parenthesis != None:
    info.append(in_parenthesis.group(0))

  # Tokenize names
  name_tokens = tokenize(register_name)
  
  # If is community the first token is info
  is_community = (register_type == 'community')
  if is_community:
    info.append(name_tokens[0])
  
  # If has a number is info
  for name_token in name_tokens:
    if contains_numbers(name_token) and (not (name_token in info)):
      info.append(name_token)
  
  return info

def tokenize(str_val):
  return [token for token in str_val.split(' ') if len(token) > 0]

def contains_numbers(str_val):
  return len(NUMBERS_GROUP.findall(str_val)) > 0
  
def replace_char_at_index(str_val, char, index):
  list_str = list(str_val)
  list_str[index] = char
  return ''.join(list_str)

def matches(pattern, str_val):
  return pattern.match(str_val) != None