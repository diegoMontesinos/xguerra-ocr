# -*- coding: utf-8 -*-

import cv2
import numpy as np
from .utils import *

def find_rows(binary_image, args):

  # Dilate image
  kernel_dilation = np.ones((1, 15), np.uint8)
  image_dilation = cv2.dilate(binary_image, kernel_dilation, iterations=1)

  if args.debug:
    show_scaled_image('rows dilation', image_dilation, 0.35)
  
  # Close image
  kernel_closing = np.ones((1, 95), np.uint8)
  image_closing = cv2.morphologyEx(image_dilation, cv2.MORPH_CLOSE, kernel_closing)

  if args.debug:
    show_scaled_image('rows closing', image_closing, 0.6)
  
  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  if args.debug:
    contours_img = draw_contours(binary_image, contours)
    show_scaled_image('contours rows', contours_img, 0.6)
  
  # Create rows and sort them
  rows = []
  for contour in contours:
    row = cv2.boundingRect(contour)

    if (is_valid_row(row)):
      rows.append(row)
  
  rows.sort(key=lambda row: row[1])
  rows.sort(key=lambda row: row[0])
  return rows

def is_valid_row(row):
  w = row[2]
  h = row[3]

  area = w * h
  return (area > 12000) and (h < 60)
