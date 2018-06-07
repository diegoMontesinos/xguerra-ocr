# -*- coding: utf-8 -*-

import re
from ..utils import matches
from ..catalogs_data import CatalogsData

class DiaryParsingException(Exception):

  MODULES_NUMBER_EXCEEDED = 1
  MODULE_TYPE_NOT_RECOGNIZED = 2
  BAD_ZONE_STRING = 3
  BAD_YEAR = 4
  INVALID_VALUE_ON_ZONE = 5
  BAD_NUM_ID = 6
  NO_ANNUARY_REGISTER = 7

  def __init__(self, message, code):
    Exception.__init__(self, message)
    self.error_code = code

class DiaryModuleParser:

  # module_type: [ (catalog, spaces), (catalog, spaces), ... ]
  MODULE_ZONES = {
    'A':  [ (30, 1), (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'BA': [ (1, 2), (2, 1), (3, 2), (5, 2), (6, 1) ],
    'BB': [ (1, 2), (2, 1), (3, 2), (7, 2), (8, 1) ],
    'BC': [ (1, 2), (10, 1), (3, 2), (9, 2), (11, 1) ],
    'BD': [ (1, 2), (2, 1), (3, 2), (9, 2), (12, 1) ],
    'BE': [ (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'BF': [ (1, 2), (13, 1), (3, 2), (5, 2), (14, 1) ],
    'BH': [ (1, 2), (2, 1), (3, 2), (5, 2), (14, 1) ],
    'BI': [ (1, 2), (2, 1), (3, 2), (16, 2), (17, 1) ],
    'BJ': [ (1, 2), (2, 1), (3, 2), (9, 2), (12, 1) ],
    'BK': [ (1, 2), (2, 1), (3, 2), (5, 2), (12, 1) ],
    'BL': [ (1, 2), (2, 1), (3, 2), (18, 2), (12, 1) ],
    'BM': [ (1, 2), (2, 1), (3, 2), (9, 2), (19, 1) ],
    'BN': [ (1, 2), (2, 1), (3, 2), (9, 2), (20, 1) ],
    'BO': [ (1, 2), (21, 1), (3, 2), (40, 2), (22, 1) ],
    'BP': [ (1, 2), (2, 1), (3, 2), (9, 2), (20, 1) ],
    'BQ': [ (1, 2), (2, 1), (3, 2), (9, 2), (12, 1) ],
    'BR': [ (1, 2), (2, 1), (3, 2), (5, 2), (23, 1) ],
    'BS': [ (1, 2), (2, 1), (3, 2), (24, 2), (12, 1) ],
    'BT': [ (1, 2), (2, 1), (3, 2), (24, 2), (12, 1) ],
    'BU': [ (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'BV': [ (1, 2), (2, 1), (3, 2), (9, 2), (8, 1) ],
    'BW': [ (1, 2), (2, 1), (3, 2), (5, 2), (20, 1) ],
    'BZ': [ (1, 2), (2, 1), (3, 2), (9, 2), (12, 1)],
    'C':  [ (0,1), (1, 2), (2, 1), (25, 2), (1, 2), (2, 1) ],
    'D':  [ (26, 1), (1, 2), (2, 1), (3, 2), (27, 2), (0,1) ],
    'E':  [ (30, 1), (1, 2), (2, 1), (0,2), (1, 2), (2, 1) ],
    'G':  [ (29, 1), (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'H':  [ (29, 1), (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'I':  [ (29, 1), (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'J':  [ (0,1), (1, 2), (2, 1), (0,2), (1, 2), (2, 1) ],
    'K':  [ (0,1), (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'L':  [ (31, 1), (1, 2), (2, 1), (0,1), (32, 4) ],
    'M':  [ (29, 1), (1, 2), (2, 1), (25, 2), (1, 2), (2, 1) ],
    'N':  [ (29, 1), (1, 2), (2, 1), (25, 2), (1, 2), (2, 1) ],
    'O':  [ (29, 1), (1, 2), (2, 1), (25, 2), (1, 2), (2, 1) ],
    'P':  [ (0,1), (1, 2), (2, 1), (0,2), (1, 2), (2, 1) ],
    'Q':  [ (29, 1), (1, 2), (2, 1), (3, 2), (9, 2), (33, 1) ],
    'S':  [ (26, 1), (1, 2), (2, 1), (3, 2), (0,2), (0,1) ],
    'T':  [ (26, 1), (1, 2), (2, 1), (3, 2), (1, 2), (2, 1) ],
    'VC': [ (1, 2), (2, 1), (3, 2), (34, 2), (35, 1) ],
    'VM': [ (1, 2), (2, 1), (3, 2), (36, 2), (37, 1) ],
    'W':  [ (38, 1), (1, 2), (2, 1), (3, 2), (5, 2), (12, 1) ],
    'X':  [ (0,1), (1, 2), (2, 1), (0,1), (42, 4) ],
    'Y':  [ (30, 1), (1, 2), (2, 1), (41, 2), (1, 2), (2, 1) ],
    'Z':  [ (30, 1), (1, 2), (2, 1), (41, 2), (1, 2), (2, 1) ],
    '=':  [ (39, 1), (1, 2), (2, 1), (3, 2), (0,2), (0,1) ]
  }

  SPACE_CHAR = '_'
  YEAR_PATTERN = re.compile(u'^[0-9]*$')
  NUM_ID_PATTERN = re.compile(u'^[0-9]*$')

  KNOWN_CATALOG_ISSUES = {
    3  : { 'NE': 'ME', 'NI': 'MI', 'NO': 'MO', 'OR': 'QR', 'OU': 'QU', 'U5': 'US',
           '5I': 'SI', '5L': 'SL', '5O': 'SO', '8C': 'BC', 'T8': 'TB', '0': 'O',
           '1': 'I', 'OF': 'DF', '6T': 'GT'
          },
    2  : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    5  : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    6  : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    7  : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    8  : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    9  : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    10 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    11 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    12 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    13 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    16 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    17 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    18 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    19 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    20 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    21 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    22 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    23 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    24 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    33 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    34 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    35 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    36 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    37 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' },
    29 : { '2': 'Z', '6': 'G', '8': 'B', '0': 'O', '1' : 'I' },
    31 : { '2': 'Z', '6': 'G', '8': 'B', '0': 'O', '1' : 'I' },
    39 : { '2': 'Z', '6': 'G', '8': 'B', '0': 'O', '1' : 'I' },
    40 : { 'O': '0', 'Z': '2', 'S': '5', 'G': '6' }
  }

  def __init__(self):
    self.catalogs_data = CatalogsData()

  def parse_modules(self, modules, annuary_data):

    if len(modules) > 3:
      msg = 'Row only should have 3 or less modules.'
      raise DiaryParsingException(msg, DiaryParsingException.MODULES_NUMBER_EXCEEDED)

    parsed_modules = []
    for module_str in modules:
      parsed_module = self.parse_module_str(module_str, annuary_data)
      parsed_modules.append(parsed_module)

    return parsed_modules
  
  def parse_module_str(self, module_str, annuary_data):

    # Search the corresponding module type
    module_type = self.get_module_type(module_str)
    if not module_type:
      msg = 'Module type not recognized: ' + module_str
      raise DiaryParsingException(msg, DiaryParsingException.MODULE_TYPE_NOT_RECOGNIZED)
    
    parsed_module = [ module_type ]

    # Try to parse each zone of module type
    zones = DiaryModuleParser.MODULE_ZONES[module_type]

    index = len(module_type)
    for zone in zones:
      size_zone = zone[1]
      zone_str = module_str[index:(index + size_zone)]

      result_zone = self.parse_zone(zone, zone_str, module_str, annuary_data)
      parsed_module.append(result_zone)

      index = index + size_zone

    return parsed_module
  
  def get_module_type(self, module_str):

    # Known issue - 8 is B at beginning
    if module_str[0] == '8':
      module_str = 'B' + module_str[1:]
    
    for module_type in DiaryModuleParser.MODULE_ZONES:
      if module_str.startswith(module_type):
        return module_type
    
    return None
  
  def parse_zone(self, zone, zone_str, module_str, annuary_data):

    if zone_str == '':
      msg = 'Zone string is empty.'
      raise DiaryParsingException(msg, DiaryParsingException.BAD_ZONE_STRING)

    catalog_id, size_zone = zone

    # Catalog 0 - whatever
    if catalog_id == 0:
      return zone_str
    
    # Catalog 1 - year
    elif catalog_id == 1:
      return self.parse_year(zone_str)

    # Catalog 27 - 9
    elif catalog_id == 27:
      catalog_id = 9
    
    # Catalog 32, 42 - Annuary
    elif catalog_id == 32 or catalog_id == 42:
      return self.search_annuary_register_by_zone_str(zone_str, annuary_data)
    
    # Other catalog
    known_issues = {}
    if catalog_id in DiaryModuleParser.KNOWN_CATALOG_ISSUES:
      known_issues = DiaryModuleParser.KNOWN_CATALOG_ISSUES[catalog_id]

    zone_str = self.fix_known_issues(known_issues, zone_str)

    catalog = self.catalogs_data.get(catalog_id)
    catalog_register = catalog.get(zone_str)

    if not catalog_register:
      msg = 'Invalid value on zone: ' + zone_str + ' in: ' + module_str
      raise DiaryParsingException(msg, DiaryParsingException.INVALID_VALUE_ON_ZONE)
    
    return zone_str
  
  def parse_year(self, year_str):

    # Known issues O -> 0, S -> 5, I -> 1
    known_issues = { 'O': '0', 'S': '5', 'I': '1', 'G': '6' }
    year_str = self.fix_known_issues(known_issues, year_str)

    # Known issues empty year
    if '_' in year_str:
      return year_str

    if not matches(DiaryModuleParser.YEAR_PATTERN, year_str):
      msg = 'Zone is not year: ' + year_str
      raise DiaryParsingException(msg, DiaryParsingException.BAD_YEAR)
    
    return year_str
  
  def search_annuary_register_by_zone_str(self, zone_str, annuary_data):

    # Known issues _ -> 0, O -> 0
    zone_str = self.fix_known_issues({ '_': '0', 'O': '0' }, zone_str)

    # Known issues '000' is a valid num id
    if '000' in zone_str:
      return zone_str

    if not matches(DiaryModuleParser.NUM_ID_PATTERN, zone_str):
      msg = 'Bad num id: ' + zone_str
      raise DiaryParsingException(msg, DiaryParsingException.BAD_NUM_ID)
    
    num_id = int(zone_str)
    annuary_register = annuary_data.search_by_num_id(num_id)

    if not annuary_register:
      msg = 'Annuary register not found with id: ' + zone_str
      raise DiaryParsingException(msg, DiaryParsingException.NO_ANNUARY_REGISTER)
    
    return zone_str
  
  def fix_known_issues(self, changes, zone_str):

    tmp = zone_str
    for bad_str in changes:
      tmp = tmp.replace(bad_str, changes[bad_str])
    
    return tmp