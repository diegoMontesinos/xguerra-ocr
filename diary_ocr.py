#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import dependencies
import pytesseract
import argparse
import cv2
import numpy as np
import os
import readline
import math
from src import AnnuaryData, DiaryData, crop_roi, show_scaled_image, \
                fix_image_rotation, binarize_image, find_columns_on_diary, \
                find_blocks_on_diary_col, parse_annuary_register_str, \
                get_diary_content_rows, AnnuaryParsingException, \
                get_tesseract_cmd, parse_num_id_only, DiaryModuleParser, \
                DiaryParsingException, draw_boxes

import time

class DiaryOCR:

  PAGE_ROI = (100, 200, 3400, 4650)
  SPACE_CHAR = '_'

  def __init__(self, args):
    self.annuary_data = AnnuaryData(args.annuary)
    self.diary_data = DiaryData(args.output)

    self.module_parser = DiaryModuleParser(self.annuary_data)

    self.input_path = args.input
    self.debug = args.debug

  def start(self):

    if not os.path.exists(self.input_path):
      print('\nError on reading or file input dont exist. ( ∩ ︵ ∩ )')
      return

    print('\nProcessing file ' + self.input_path + '...')

    # Read image source and crop it
    image_src = cv2.imread(self.input_path)
    image_src = crop_roi(image_src, DiaryOCR.PAGE_ROI)
    image_src = fix_image_rotation(image_src)
    if self.debug:
      show_scaled_image('source', image_src, 0.4)
    
    # Get binary image
    binary_image = binarize_image(image_src)
    if self.debug:
      show_scaled_image('binary', binary_image, 0.4)
    
    # Get columns
    cols = find_columns_on_diary(binary_image, self.debug)
    print('Detected ' + str(len(cols)) + ' columns.')

    # Process each column
    for i in range(len(cols)):
      print('\nProcessing ' + str(i + 1) + '/' + str(len(cols)) + ' column...')

      img_col = crop_roi(binary_image, cols[i])
      self.process_col(img_col)
  
  def process_col(self, img_col):

    if self.debug:
      show_scaled_image('col', img_col, 0.4)
    
    # Find blocks from the column
    blocks = find_blocks_on_diary_col(img_col, self.debug)
    print('  Detected ' + str(len(blocks)) + ' blocks.')

    # Process each block
    for block in blocks:
      self.process_block(img_col, block)
  
  def process_block(self, img_col, block):

    print('\n  :::::::::')

    # Get header
    header_img = crop_roi(img_col, block[0])
    header_register = self.read_header(header_img)
    annuary_id = header_register['num_id']

    print('  * Annuary register: ' + str(header_register))

    # Check if has content
    has_content = (block[1] != None)
    if not has_content:
      return
    
    # Check if is already readed (prevent repeat work)
    stored_content = self.diary_data.search_by_annuary_id(annuary_id)
    if (stored_content != None) and (len(stored_content) > 0):
      return
    
    # Get content
    content_img = crop_roi(img_col, block[1])
    content = self.read_content(content_img)

    # Register content
    print('  * Content: ')
    for module in content:
      self.diary_data.add_module(annuary_id, module)
      print('    - ' + ''.join(module))

  def read_header(self, header_img):

    # Execute OCR with custom config
    config_str = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+*.() --psm 7'
    bytes_readed = pytesseract.image_to_string(header_img, config=config_str)
    readed_str = bytes_readed.encode('utf-8')

    return self.process_annuary_str(header_img, readed_str)

  def process_annuary_str(self, header_img, readed_str):

    # Try parse header and catch errors
    try:
      readed_register = parse_annuary_register_str(readed_str)

      num_id = readed_register['num_id']
      annuary_register = self.annuary_data.search_by_num_id(num_id)

      # Not registered
      if not annuary_register:
        self.annuary_data.add_register(readed_register)
        return readed_register
      
      # Registered but not equal
      elif not self.are_registers_equals(readed_register, annuary_register):
        return self.choose_register(header_img, readed_register, annuary_register)

      # Registered
      else:
        return readed_register

    except AnnuaryParsingException as exception:
      return self.fix_annuary_register(header_img, readed_str, exception)
  
  def are_registers_equals(self, register_a, register_b):
    return (register_a['text_id'] == register_b['text_id']) and \
           (register_a['info'] == register_b['info']) and \
           (register_a['type'] == register_b['type']) and \
           (register_a['name'] == register_b['name'])
  
  def choose_register(self, header_img, register_a, register_b):

    # Get option from user
    print('\n  Differences were found in registers.')
    print('      1. ' + str(register_a))
    print('      2. ' + str(register_b))

    # Show image
    cv2.imshow('Header', header_img)
    while cv2.waitKey(0) != ord('c'):
      pass

    user_input = raw_input('  Help me to choose one: ')
    if user_input == '1':
      choosed = register_a
    else:
      choosed = register_b
    
    # Close image and update in data
    cv2.destroyAllWindows()
    
    self.annuary_data.update_register(choosed)

    return choosed

  def fix_annuary_register(self, header_img, readed_str, exception):

    annuary_register = None

    if AnnuaryParsingException.BAD_NUMERIC_ID != exception.error_code:
      try:
        num_id = parse_num_id_only(readed_str)
        annuary_register = self.annuary_data.search_by_num_id(num_id)
      except AnnuaryParsingException as exception:
        annuary_register = None
    
    user_should_fix = not annuary_register
    if user_should_fix:
      return self.user_fix_annuary_error(header_img, exception)

    return annuary_register
  
  def user_fix_annuary_error(self, header_img, exception):
    print('  ---\n  ANNUARY ERROR: ' + str(exception) + '. Help me to fix it.')

    # Show image
    cv2.imshow('Header', header_img)
    while cv2.waitKey(0) != ord('c'):
      pass

    user_input = raw_input('  Enter the fixed register: ')
    cv2.destroyAllWindows()

    return self.process_annuary_str(header_img, user_input)

  def read_content(self, content_img):

    if self.debug:
      show_scaled_image('content', content_img, 1.0)
    
    # Get each content row
    content_rows = get_diary_content_rows(content_img, self.debug)

    # Process each content row
    content = []
    for content_row in content_rows:
      content += self.process_content_row(content_img, content_row)
    
    return content

  def process_content_row(self, content_img, content_row):

    row_modules = content_row['modules']
    row = content_row['row']

    # Crop and read the content
    row_img = crop_roi(content_img, row)
    row_str = self.read_content_row(row_img, row_modules)

    return self.process_content_row_str(content_img, row, row_str)

  def read_content_row(self, row_img, row_modules):
    row_str = ''

    for content_module in row_modules:
      num_chars, char_rect = content_module

      if not char_rect:
        row_str += (DiaryOCR.SPACE_CHAR * num_chars)
        continue
      
      # Execute OCR
      char_img = crop_roi(row_img, char_rect)

      config_str = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789= --psm 8'
      
      bytes_readed = pytesseract.image_to_string(char_img, config=config_str)
      readed_str = bytes_readed.encode('utf-8')

      row_str += readed_str
    
    if len(row_str) < 33:
      missing_spaces = 11 - (len(row_str) % 11)
      for i in range(missing_spaces):
        row_str += DiaryOCR.SPACE_CHAR
    
    return row_str
  
  def process_content_row_str(self, content_img, row, row_str, skipping={}):
    
    # Parse row_str into modules
    modules = self.slice_row_str(row_str)
    try:
      parsed_modules = self.module_parser.parse_modules(modules, skipping)
    except DiaryParsingException as exception:
      return self.user_fix_modules_error(content_img, row, row_str, exception, skipping)
    
    return parsed_modules
  
  def slice_row_str(self, row_str):

    modules = []

    num_modules = int(math.ceil(len(row_str) / 11.0))
    for i in range(num_modules):
      init = i * 11
      stop = init + 10
      modules.append(row_str[init:stop])

    return modules

  def user_fix_modules_error(self, content_img, row, row_str, exception, skipping):
    print('  ---\n  DIARY ERROR: ' + str(exception) + '. Help me to fix it.')

    # Show image
    show_row_img = draw_boxes(content_img, [ row ], (0, 255, 0))
    cv2.imshow('Content row image', show_row_img)
    while cv2.waitKey(0) != ord('c'):
      pass

    user_input = raw_input(' [' + row_str + '] Enter the fixed text: ')
    cv2.destroyAllWindows()

    # User try to skip the exception
    if (user_input == 'SKIP'):
      could_skip_exception = (exception.num_module != -1) and (exception.zone != None)

      if could_skip_exception:
        skipping = self.skip_exception(skipping, exception)
        return self.process_content_row_str(content_img, row, row_str, skipping)

      else:
        print('  You cant skip this exception.')
        return self.user_fix_modules_error(content_img, row, row_str, exception, skipping)
    
    return self.process_content_row_str(content_img, row, user_input, skipping)
  
  def skip_exception(self, skipping, exception):

    if not exception.num_module in skipping:
      skipping[exception.num_module] = []
      
    skipping[exception.num_module].append(exception)

    return skipping
  
  def save_data(self):
    print('\n\n  Saving data...')

    self.annuary_data.save()
    self.diary_data.save()

def print_welcome_message():
  print('\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
  print('::                      DIARY OCR                      ::')
  print(':: A digitalization of the diary section from the      ::')
  print(':: Francoise Xavier Guerra database.                   ::')
  print('::                                                     ::')
  print(':: Lucía Granados (luciagranadosriveros@gmail.com)     ::')
  print(':: Diego Montesinos (diegomontesinos@ciencias.unam.mx) ::')
  print(':::::::::::::::::::::::::::::::::::::::::::::::::::::::::')

# Main script
def main():

  # Check tesseract installation
  tesseract_cmd = get_tesseract_cmd()
  if (not tesseract_cmd) or (tesseract_cmd == ''):
    print('Tesseract not installed')
    return
  
  pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

  # Parse args
  parser = argparse.ArgumentParser(description='A digitalization of diary section from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file')
  parser.add_argument('-a', '--annuary', help='Annuary CSV file', default='csv/annuary.csv')
  parser.add_argument('-o', '--output', help='Output CSV file', default='csv/diary.csv')
  parser.add_argument('-d', '--debug', help='Enable debug option', action='store_true')

  args = parser.parse_args()
  
  if not args.input:
    print('error: argument -i/--input is required')
    return
  
  init_ts = time.time()
  
  #print_welcome_message()

  # Create OCR and run
  ocr = DiaryOCR(args)
  try:
    ocr.start()
    ocr.save_data()
  except KeyboardInterrupt:
    ocr.save_data()

  duration = time.time() - init_ts
  print('\n  Finished at ' + str(duration) + ' seconds.')

if __name__ == '__main__':
  main()
