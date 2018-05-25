#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import dependencies
import pytesseract
import argparse
import cv2
import numpy as np
import os
from src import AnnuaryData, crop_roi, show_scaled_image, fix_image_rotation, \
                binarize_image, find_columns_on_diary, find_blocks_on_diary_col, \
                parse_annuary_register_str, AnnuaryParsingException, get_tesseract_cmd, \
                find_diary_content_modules

PAGE_ROI = (100, 200, 3400, 4650)

class DiaryOCR:

  def __init__(self, args):
    self.annuary_data = AnnuaryData(args.annuary)
    #self.diary_data = DiaryData(args.diary)

    self.input_path = args.input
    self.debug = args.debug

  def start(self):
    print('Processing file ' + self.input_path + '...')

    if not os.path.exists(self.input_path):
      print('Error on reading or file input dont exist. ( ∩ ︵ ∩ )')
      return
  
    # Read image source and crop it
    image_src = cv2.imread(self.input_path)
    image_src = crop_roi(image_src, PAGE_ROI)
    image_src = fix_image_rotation(image_src)
    if self.debug:
      show_scaled_image('source', image_src, 0.4)
    
    # Get binary image
    binary_image = binarize_image(image_src)
    if self.debug:
      show_scaled_image('binary', binary_image, 0.4)
    
    # Get columns
    cols = find_columns_on_diary(binary_image, self.debug)
    for col in cols:
      img_col = crop_roi(binary_image, col)
      self.process_col(img_col)
  
  def process_col(self, img_col):

    if self.debug:
      show_scaled_image('col', img_col, 0.4)

    # Find blocks from the col
    blocks = find_blocks_on_diary_col(img_col, self.debug)
    for block in blocks:
      self.process_block(img_col, block)
  
  def process_block(self, img_col, block):

    # Get header
    header_img = crop_roi(img_col, block[0])
    header_register = self.read_header(header_img)

    has_content = (block[1] != None)
    if not has_content:
      return

    # Get content
    #content_img = crop_roi(img_col, block[1])
    #content = self.read_content(content_img)

    # Register in data
    #self.add_content(header_register, content)

  def read_header(self, header_img):

    # Execute OCR with custom config
    config_str = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+*.() --psm 7'
    bytes_readed = pytesseract.image_to_string(header_img, config=config_str)
    readed_str = bytes_readed.encode('utf-8')

    # Try parse header and catch errors
    try:
      readed_register = parse_annuary_register_str(readed_str)

      num_id = readed_register['num_id']
      annuary_register = self.annuary_data.search_by_num_id(num_id)

      # Not registered
      if not annuary_register:
        self.annuary_data.add_register(readed_register)
        print('Added register: ' + str(readed_register))
        
        return readed_register
      
      # Registered but not equal
      elif not self.are_registers_equals(readed_register, annuary_register):
        return self.choose_register(readed_register, annuary_register)
      
      # Registered
      else:
        return readed_register

    except AnnuaryParsingException as exception:
      return self.fix_annuary_register(exception)
  
  def are_registers_equals(self, register_a, register_b):
    return (register_a['text_id'] == register_b['text_id']) and \
           (register_a['info'] == register_b['info']) and \
           (register_a['type'] == register_b['type']) and \
           (register_a['name'] == register_b['name'])
  
  def choose_register(self, register_a, register_b):
    print register_a
    print register_b
  
  def fix_annuary_register(self, exception):
    print exception

  def read_content(self, content_img):

    if self.debug:
      show_scaled_image('content', content_img, 1.0)
    
    content_modules = find_diary_content_modules(content_img, self.debug)
    
    for content_module in content_modules:
      module_str = self.read_content_module(content_img, content_module)
      modules = self.slice_module_str(module_str)

  def read_content_module(self, content_img, content_module):
    module_str = ''

    for char_module in content_module:
      num_chars, char_rect = char_module

      if not char_rect:
        for i in range(num_chars):
          module_str += ' '
        continue
      
      # Execute OCR
      char_img = crop_roi(content_img, char_rect)

      config_str = '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789= '
      if num_chars > 1:
        config_str += ' --psm 8'
      else:
        config_str += ' --psm 10'
      
      bytes_readed = pytesseract.image_to_string(char_img, config=config_str)
      readed_str = bytes_readed.encode('utf-8')

      module_str += readed_str

    missing_spaces = 11 - (len(module_str) % 11)
    for i in range(missing_spaces):
      module_str += ' '
    
    return module_str
  
  def slice_module_str(self, module_str):

    modules = []

    num_modules = len(module_str) / 11
    for i in range(num_modules):
      init = i * 11
      stop = init + 10
      modules.append(module_str[init:stop])

    return modules

def print_welcome_message():
  print('\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
  print('::                      DIARY OCR                      ::')
  print(':: A digitalization of the diary section from the      ::')
  print(':: Francoise Xavier Guerra database.                   ::')
  print('::                                                     ::')
  print(':: Lucía Granados (luciagranadosriveros@gmail.com)     ::')
  print(':: Diego Montesinos (diegomontesinos@ciencias.unam.mx) ::')
  print(':::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n')

# Main script
def main():

  # Check tesseract installation
  tesseract_cmd = get_tesseract_cmd()
  if (not tesseract_cmd) or (tesseract_cmd == ''):
    return
  
  pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

  # Parse args
  parser = argparse.ArgumentParser(description='A digitalization of diary section from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file')
  parser.add_argument('-a', '--annuary', help='Annuary CSV file', default='csv/annuary.csv')
  parser.add_argument('-d', '--debug', help='Enable debug option', action='store_true')

  args = parser.parse_args()

  if not args.input:
    print('error: argument -i/--input is required')
    return
  
  #print_welcome_message()
  
  # Create OCR and run
  ocr = DiaryOCR(args)
  ocr.start()

if __name__ == '__main__':
  main()
