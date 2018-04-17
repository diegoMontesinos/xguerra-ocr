#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import dependencies
import pytesseract
import argparse
import cv2
from src import *

def process_rows(binary_image, rows, args):
  print('Process rows and dump into ' + args.output)

  bad_count = 0

  for i, row in enumerate(rows):
    x, y, w, h = row
    
    roi = binary_image[y:y+h, x:x+w]

    readed = pytesseract.image_to_string(roi)
    register_str = readed.encode('utf-8')

    try:
      register = parse_register_str(register_str)
    except Exception as e:
      print '\n'
      print e
      show_scaled_image('Row: ' + str(i), roi, 1.0, wait=False)
      user_input = raw_input()
      register = parse_register_str(user_input)
      print user_input
      
      bad_count += 1
    
    print register
  
  print('Errors in: ' + str(bad_count) + ' registers of: ' + str(len(rows)))

def process_image(args):
  print('Processing file ' + args.input + '...')

  # Read image source
  print('Readed image source.')
  image_src = cv2.imread(args.input)
  if args.debug:
    show_scaled_image('source', image_src, 0.35)

  # Get binary image
  binary_image = binarize_image(image_src)
  if args.debug:
    show_scaled_image('binary', binary_image, 0.35)

  # Get rows
  rows = find_rows(binary_image, args)
  print('Finded ' + str(len(rows)) + ' rows.')

  if args.debug:
    boxes_img = draw_boxes(binary_image, rows, (0, 255, 0))
    show_scaled_image('rows', boxes_img, 0.35)
  
  # Process rows
  process_rows(binary_image, rows, args)

# Main script
def main():

  # Config parser
  parser = argparse.ArgumentParser(description='Digitalization of Annuary-part from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file', required=True)
  parser.add_argument('-o', '--output', help='Output text file', default='output.txt')
  parser.add_argument('-d', '--debug', help='Debug parameter', action='store_true')

  args = parser.parse_args()
  process_image(args)

if __name__ == '__main__':
  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
  main()
