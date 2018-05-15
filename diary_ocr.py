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
                find_diary_content

PAGE_ROI = (100, 200, 3400, 4650)

class DiaryOCR:

  def __init__(self, args):
    self.annuary_data = AnnuaryData(args.annuary)
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
    has_header = (block[1] != None)
    if not has_header:
      return

    # Get header and content image with ROI
    header_img = crop_roi(img_col, block[0])
    content_img = crop_roi(img_col, block[1])

    self.read_content(content_img)

  def read_header(self, header_img):

    # Execute OCR
    bytes_readed = pytesseract.image_to_string(header_img)
    readed_str = bytes_readed.encode('utf-8')

    # Try parse header and catch errors
    try:
      readed_register = parse_annuary_register_str(readed_str)
      num_id = readed_register['num_id']

      annuary_register = self.annuary_data.search_by_num_id(num_id)

      if not annuary_register:
        print 'No esta registrado! :O'
      else:
        print readed_register
        print annuary_register
    
    except AnnuaryParsingException as exception:
      print exception
    
    print '--'
  
  def read_content(self, content_img):
    #show_scaled_image('content', content_img, 1.0)
    find_diary_content(content_img, self.debug)

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
