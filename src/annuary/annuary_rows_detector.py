# -*- coding: utf-8 -*-

import numpy as np
import cv2
from ..utils import *

MAX_WIDTH_ROW = 1030
MIN_ROW_AREA = 12000
MAX_HEIGHT_ROW = 60

def find_rows_on_annuary(binary_image, args):

  # Dilate image
  kernel_dilation = np.ones((1, 15), np.uint8)
  image_dilation = cv2.dilate(binary_image, kernel_dilation, iterations=1)

  if args.debug:
    show_scaled_image('rows dilation', image_dilation, 0.4)
  
  # Close image
  kernel_closing = np.ones((1, 95), np.uint8)
  image_closing = cv2.morphologyEx(image_dilation, cv2.MORPH_CLOSE, kernel_closing)

  if args.debug:
    show_scaled_image('rows closing', image_closing, 0.4)
  
  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  if args.debug:
    contours_img = draw_contours(binary_image, contours)
    show_scaled_image('contours rows', contours_img, 0.4)

  # Create rows and sort them
  rows = []
  for contour in contours:
    row = cv2.boundingRect(contour)

    if not is_valid_annuary_row(row):
      continue

    x, y, w, h = row
    if w >= MAX_WIDTH_ROW:
      rows.append((x, y, MAX_WIDTH_ROW, h))
      rows.append((x + MAX_WIDTH_ROW + 3, y, w - MAX_WIDTH_ROW, h))
    else:
      rows.append(row)
  
  rows.sort(key=lambda row: row[1])
  rows.sort(key=lambda row: row[0])
  
  return rows

def is_valid_annuary_row(row):
  w = row[2]
  h = row[3]

  area = w * h
  return (area >= MIN_ROW_AREA) and (h <= MAX_HEIGHT_ROW)
