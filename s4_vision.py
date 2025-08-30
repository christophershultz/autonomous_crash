import pandas as pd
import numpy as np
import os, pdb, sys, pickle

df = pd.read_csv('combined_dataset.csv', sep = "~")


import fitz  # PyMuPDF
import numpy as np
import cv2
from pathlib import Path

def render_page(pdf_path, page_num=0, zoom=3.0):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    return img, page

def crop_damage_diagram(img, page, zoom_from_img=True):
    # locate "Shade in Damaged Area" then crop below it (works on DMV forms)
    hits = page.search_for("Shade in Damaged Area")
    if hits:
        rect = hits[0]
        zx = img.shape[1] / page.rect.width
        zy = img.shape[0] / page.rect.height
        x0, y0, x1, y1 = int(rect.x0*zx), int(rect.y0*zy), int(rect.x1*zx), int(rect.y1*zy)
        top    = y1 + int(25*zy)
        bottom = top + int(280*zy)
        left   = max(0, x0 - int(140*zx))
        right  = min(img.shape[1], x1 + int(140*zx))
        crop = img[top:bottom, left:right]
        if crop.size: return crop
    # fallback crop if the search fails
    h, w = img.shape[:2]
    return img[int(0.28*h):int(0.55*h), int(0.08*w):int(0.92*w)]

def band_booleans(crop, ink_thresh=110, density_cutoff=0.035):
    """
    Returns booleans for Front/Back/Left/Right by dark-ink density in bands.
    Front=top third; Back=bottom third; Left=left third; Right=right third.
    Bands overlap, so multiple True is expected for corner hits.
    """
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    _, bin_img = cv2.threshold(blur, ink_thresh, 255, cv2.THRESH_BINARY_INV)

    # remove thin outlines
    opened = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=1)

    h, w = opened.shape
    th, tw = h // 3, w // 3

    bands = {
        "front":  opened[:th, :],
        "back":   opened[-th:, :],
        "left":   opened[:, :tw],
        "right":  opened[:, -tw:]
    }

    out = {}
    for k, m in bands.items():
        density = (m > 0).sum() / m.size
        out[k] = density >= density_cutoff
        out[k+"_density"] = round(float(density), 4)
    return out

def extract_damage_bands(pdf_path, page_num=0, ink_thresh=110, density_cutoff=0.035):
    img, page = render_page(pdf_path, page_num)
    crop = crop_damage_diagram(img, page)
    return band_booleans(crop, ink_thresh, density_cutoff)

# Example:
back, front, left, right = [], [], [], []
for file in df['filename']: 
    try: 
        print(file)
        res = extract_damage_bands(file, page_num=0)
        back.append(res['back'])
        front.append(res['front'])
        left.append(res['left'])
        right.append(res['right'])
    except: 
        back.append(None)
        front.append(None)
        left.append(None)
        right.append(None)

df['damage_back'] = back
df['damage_front'] = front
df['damage_left'] = left
df['damage_right'] = right
df.to_csv('combined_dataset_with_vision.csv', index=None, sep="~")
