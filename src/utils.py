# -*- coding: utf-8 -*-

import cv2
import numpy as np
from subprocess import check_output

def get_tesseract_cmd():
  try:
    cmd = check_output(['which', 'tesseract'])
  except Exception as exception:
    return ''
  
  return cmd.replace('\n', '')

def crop_roi(image_src, roi):
  x, y, w, h = roi
  return image_src[y:y+h, x:x+w]

def show_scaled_image(title, img, scale):

  height, width = img.shape[:2]
  resized = cv2.resize(img, (0, 0), None, scale, scale)

  cv2.imshow(title, resized)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def binarize_image(image_src):

  gray = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
  ret, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

  return binary

def draw_contours(binary_image, contours):
  channel = cv2.split(binary_image)[0]

  contours_img = cv2.merge((channel, channel, channel))
  cv2.drawContours(contours_img, contours, -1, (0, 255, 0), 2)

  return contours_img

def draw_boxes(img, boxes, stroke):
  channels = cv2.split(img)

  if len(channels) == 1:
    channel = channels[0]
    boxes_img = cv2.merge((channel, channel, channel))
  else:
    boxes_img = img

  for box in boxes:
    x, y, w, h = box
    cv2.rectangle(boxes_img, (x, y), (x + w, y + h), stroke, 2)
  
  return boxes_img

def fix_image_rotation(img):
  rot_angle = get_img_angle_rotation(img)
  if abs(rot_angle) > 0.4:

    (h, w) = img.shape[:2]
    center = (w // 2, 0)
    M = cv2.getRotationMatrix2D(center, -rot_angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
  else:
    return img

def get_img_angle_rotation(img):
  binary_image = binarize_image(img)

  kernel_close = np.ones((75, 150), np.uint8)
  image_close = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel_close)

  im2, contours, hierarchy = cv2.findContours(image_close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  ctrs = []

  angle_sum = 0.0
  count = 0.0
  for contour in contours:
    area = cv2.contourArea(contour)

    if area > 400000:
      angle = get_angle_contour(contour)

      angle_sum += angle
      count += 1.0

  return (angle_sum / count)

def get_angle_contour(contour):
  angle = cv2.minAreaRect(contour)[-1]

  if angle < -45:
    angle = -(90 + angle)
  else:
    angle = -angle
  
  return angle