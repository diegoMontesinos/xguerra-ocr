# -*- coding: utf-8 -*-

import numpy as np
import cv2
from ..utils import *

COL_WIDTH = 1035
MIN_COL_HEIGHT = 1000
MIN_COL_WIDTH = 40
MIN_DISTANCE = 20
MIN_ROW_AREA = 7700
MAX_HEIGHT_ROW = 60
MAX_X_ROW = 40

def find_columns_on_annuary(binary_image, args):

  # Dilate image
  kernel_dilation = np.ones((60, 25), np.uint8)
  image_dilation = cv2.dilate(binary_image, kernel_dilation, iterations=1)

  if args.debug:
    show_scaled_image('cols dilation', image_dilation, 0.4)

  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  contours_img = draw_contours(binary_image, contours)

  if args.debug:
    show_scaled_image('contours cols', contours_img, 0.4)

  # Get bounding boxes as detected columns
  detected_cols = []
  for contour in contours:
    col = cv2.boundingRect(contour)

    if is_valid_annuary_col(col):
      detected_cols.append(col)
  
  # Sort by x
  detected_cols.sort(key=lambda col: col[0])

  # Get first and second in x-order and create cols
  first = detected_cols[0]
  second = detected_cols[1]

  height, width = binary_image.shape[:2]

  cols = get_columns_from(first, width)
  if abs(first[0] - second[0]) <= MIN_DISTANCE:
    cols += get_columns_from(second, width)

  if args.debug:
    boxes_img = draw_boxes(binary_image, cols, (0, 255, 0))
    show_scaled_image('cols', boxes_img, 0.4)

  return cols

def get_columns_from(left_col, width):
  left_x, left_y, left_w, left_h = left_col

  cols = [
    (left_x, left_y, COL_WIDTH, left_h),
    (left_x + COL_WIDTH, left_y, COL_WIDTH, left_h),
    (left_x + (2 * COL_WIDTH), left_y, width - (left_x + (2 * COL_WIDTH)), left_h)
  ]
  
  return cols

def is_valid_annuary_col(col):
  w = col[2]
  h = col[3]
  ratio = float(w) / float(h)

  return (ratio < 1.0) and (h > MIN_COL_HEIGHT) and (w > MIN_COL_WIDTH)

def find_rows_on_annuary(binary_image, args):

  # Dilate image
  kernel_dilation = np.ones((1, 50), np.uint8)
  image_dilation = cv2.dilate(binary_image, kernel_dilation, iterations=1)

  if args.debug:
    show_scaled_image('rows dilation', image_dilation, 0.4)
  
  # Close image
  kernel_closing = np.ones((1, 180), np.uint8)
  image_closing = cv2.morphologyEx(image_dilation, cv2.MORPH_CLOSE, kernel_closing)

  if args.debug:
    show_scaled_image('rows closing', image_closing, 0.4)
  
  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  if args.debug:
    contours_img = draw_contours(binary_image, contours)
    show_scaled_image('contours rows', contours_img, 0.4)

  # Create rows and sort them
  height, width = binary_image.shape[:2]

  rows = []
  for contour in contours:
    row = cv2.boundingRect(contour)

    if not is_valid_annuary_row(row):
      continue
    
    x, y, w, h = row
    rows.append((x, y, width, h))
  
  rows.sort(key=lambda row: row[1])

  if args.debug:
    boxes_img = draw_boxes(binary_image, rows, (0, 255, 0))
    show_scaled_image('rows', boxes_img, 0.4)
  
  return rows

def is_valid_annuary_row(row):
  x = row[0]
  w = row[2]
  h = row[3]

  area = w * h
  return (x <= MAX_X_ROW) and (area >= MIN_ROW_AREA) and (h <= MAX_HEIGHT_ROW)
