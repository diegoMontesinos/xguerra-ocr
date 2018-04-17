# -*- coding: utf-8 -*-

import re

ONLY_NUMBERS           = re.compile(u'^[0-9]*$')
ONLY_UPPERCASE_DOTS    = re.compile(u'^[A-Z. \(\)]*$')
ONLY_UPPERCASE_LETTERS = re.compile(u'^[A-Z]*$')

class AnnuaryRegisterParser():

  def __init__(self):
    pass
  
  def parse_register_str(register_str):
    tokens = register_str.split(' ')

    if '\n' in register_str:
      raise Exception('Register contains breakline, should be a line')
      print('Here!!!!')

    if len(tokens) < 3:
      raise Exception('Insuficient tokens at register: ' + register_str)
    
    register_id = get_register_id(tokens)

    index_id = len(tokens[0]) + len(tokens[1]) + 1
    name = register_str[index_id:].strip()
    name = name.replace(',', '.')

    if ONLY_UPPERCASE_DOTS.match(name) == None:
      raise Exception('Invalid name: ' + name)

    return { 'id' : register_id, 'name' : name }

  def get_register_id(tokens):

    # Get and validate id
    letters_id = tokens[0]
    numbers_id = tokens[1]

    if (ONLY_UPPERCASE_LETTERS.match(letters_id) == None) or (len(letters_id) < 2):
      raise Exception('Bad letters id: ' + letters_id)
    
    if ONLY_NUMBERS.match(numbers_id) == None:
      raise Exception('Bad numbers id: ' + numbers_id)
    
    return (letters_id, int(numbers_id))
