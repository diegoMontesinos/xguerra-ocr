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
                parse_register_str

PAGE_ROI = (100, 200, 3400, 4650)

def process_image(args, annuary_data):
  print('Processing file ' + args.input + '...')

  if not os.path.exists(args.input):
    print('Error on reading or file input dont exist. ( ∩ ︵ ∩ )')
    return
  
  # Read image source and crop it
  image_src = cv2.imread(args.input)
  image_src = crop_roi(image_src, PAGE_ROI)
  image_src = fix_image_rotation(image_src)
  
  if args.debug:
    show_scaled_image('source', image_src, 0.4)

  # Get binary image
  binary_image = binarize_image(image_src)
  if args.debug:
    show_scaled_image('binary', binary_image, 0.4)
    
  # Get columns
  cols = find_columns_on_diary(binary_image, args.debug)

  for col in cols:
    img_col = crop_roi(binary_image, col)
    process_col(img_col, annuary_data, args)

def process_col(img_col, annuary_data, args):

  if args.debug:
    show_scaled_image('col', img_col, 0.4)

  # Find blocks from the col
  blocks = find_blocks_on_diary_col(img_col, args.debug)

  bad = 0
  for block in blocks:

    # Get header ROI and execute OCR
    header_img = crop_roi(img_col, block[0])

    readed = pytesseract.image_to_string(header_img)
    register_str = readed.encode('utf-8')

    # Try parse header and catch errors
    try:
      register = parse_register_str(register_str)
      #img_col
    except Exception as exception:
      bad += 1
  
  print bad
  print len(blocks)
  print '--'

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

  # Config parser
  parser = argparse.ArgumentParser(description='A digitalization of diary section from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file')
  parser.add_argument('-a', '--annuary', help='Annuary CSV file', default='csv/annuary.csv')
  parser.add_argument('-d', '--debug', help='Enable debug option', action='store_true')

  args = parser.parse_args()

  if not args.input:
    print('error: argument -i/--input is required')
    return
  
  #print_welcome_message()

  annuary_data = AnnuaryData(args.annuary)

  process_image(args, annuary_data)

if __name__ == '__main__':

  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
  main()
