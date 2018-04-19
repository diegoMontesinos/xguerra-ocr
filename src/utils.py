# -*- coding: utf-8 -*-

import cv2

def show_scaled_image(title, img, scale):

  height, width = img.shape[:2]
  resized = cv2.resize(img, (0, 0), None, scale, scale)

  cv2.imshow(title, resized)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def binarize_image(image_src):

  gray = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
  ret, binary = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)

  return binary

def draw_contours(binary_image, contours):
  channel = cv2.split(binary_image)[0]

  contours_img = cv2.merge((channel, channel, channel))
  cv2.drawContours(contours_img, contours, -1, (0, 255, 0), 2)

  return contours_img

def draw_boxes(binary_image, boxes, stroke):
  channel = cv2.split(binary_image)[0]

  boxes_img = cv2.merge((channel, channel, channel))
  for box in boxes:
    x, y, w, h = box
    cv2.rectangle(boxes_img, (x, y), (x + w, y + h), stroke, 1)
  
  return boxes_img
