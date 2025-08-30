import pandas as pd
import numpy as np
import os, pdb, sys, pickle

df = pd.read_csv('combined_dataset.csv', sep = "~")


import fitz, cv2, numpy as np

# ---------- 1) render + crop the damage diagram ----------
def render_and_crop(pdf_path, page_num=0, zoom=3.0):
    doc = fitz.open(pdf_path); page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
    # locate heading
    hits = page.search_for("Shade in Damaged Area")
    if hits:
        zx, zy = img.shape[1]/page.rect.width, img.shape[0]/page.rect.height
        r = hits[0]
        x0,y0,x1,y1 = int(r.x0*zx),int(r.y0*zy),int(r.x1*zx),int(r.y1*zy)
        top    = y1 + int(25*zy)
        bottom = top + int(280*zy)
        left   = max(0, x0 - int(140*zx))
        right  = min(img.shape[1], x1 + int(140*zx))
        crop = img[top:bottom, left:right]
        if crop.size: return crop
    # fallback
    h,w = img.shape[:2]
    return img[int(0.28*h):int(0.55*h), int(0.08*w):int(0.92*w)]

# ---------- 2) find the small squares along edges ----------
import cv2, numpy as np

def find_seat_squares(crop):
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)
    g = cv2.GaussianBlur(g, (5,5), 0)
    _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    cnts,_ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    H,W = bw.shape
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        A = w*h
        if A < 250 or A > 0.03*H*W: 
            continue
        # near-square and rectangular
        ar = w/float(h)
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.08*peri, True)
        if 0.7 < ar < 1.3 and len(approx) in (4,5):
            # prefer hollow squares (seat boxes)
            pad = max(2, int(0.12*min(w,h)))
            inner = bw[y+pad:y+h-pad, x+pad:x+w-pad]
            if inner.size and inner.mean() < 80:
                boxes.append((x,y,w,h))
    return boxes, bw

def has_x(roi, min_len_frac=0.55, center_tol=0.22, angle_tol_deg=25):
    """Detect two diagonals crossing near center via Hough lines."""
    roi = cv2.resize(roi, (64,64), interpolation=cv2.INTER_AREA)
    # emphasize strokes, suppress border
    k = np.ones((3,3), np.uint8)
    roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, k, iterations=1)
    edges = cv2.Canny(roi, 60, 140)

    # Hough lines
    L = []
    for thr in (28, 24, 20):  # relax stepwise
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=thr,
                                minLineLength=18, maxLineGap=6)
        if lines is not None:
            for x1,y1,x2,y2 in lines[:,0]:
                dx, dy = x2-x1, y2-y1
                ang = np.degrees(np.arctan2(dy, dx)) % 180
                # keep near-diagonals (≈45° or 135°)
                if min(abs(ang-45), abs(ang-135)) <= angle_tol_deg:
                    L.append((x1,y1,x2,y2,ang))
        if L: break
    if len(L) < 2: 
        return False, 0.0

    # choose two longest diagonals that intersect near the center
    def length(p): 
        x1,y1,x2,y2,_ = p; return np.hypot(x2-x1, y2-y1)
    L.sort(key=length, reverse=True)
    best_score = 0.0
    H = W = 64
    min_len = min_len_frac * np.hypot(W, H)
    cx, cy = W/2, H/2

    for i in range(len(L)):
        for j in range(i+1, len(L)):
            (x1,y1,x2,y2,a1) = L[i]; (x3,y3,x4,y4,a2) = L[j]
            # angle difference ~90°
            if abs(((a1-a2+90)%180)-90) > angle_tol_deg: 
                continue
            # compute intersection
            A = np.array([[x2-x1, x3-x4],[y2-y1, y3-y4]], dtype=float)
            b = np.array([x3-x1, y3-y1], dtype=float)
            if abs(np.linalg.det(A)) < 1e-3: 
                continue
            t,u = np.linalg.solve(A, b)
            xi, yi = x1 + t*(x2-x1), y1 + t*(y2-y1)
            # center proximity
            if max(abs(xi-cx)/W, abs(yi-cy)/H) > center_tol:
                continue
            # length check
            if length(L[i]) < min_len or length(L[j]) < min_len:
                continue
            # score = normalized lengths product
            s = (length(L[i])*length(L[j]))/(W*H)
            best_score = max(best_score, s)
    return (best_score > 0), float(best_score)


# ---------- 4) region masks (your colors → labels) ----------
# red  -> "right"  (bottom band)
# purple -> "left" (top band)
# blue -> "front"  (right vertical band)
# green -> "back"  (left vertical band)
def region_masks(shape):
    h,w = shape
    th, tw = int(0.30*h), int(0.26*w)  # band thicknesses (tune if needed)
    m = {
        "right": np.zeros((h,w), np.uint8),
        "left":  np.zeros((h,w), np.uint8),
        "front": np.zeros((h,w), np.uint8),
        "back":  np.zeros((h,w), np.uint8),
    }
    m["left"] [:th, :]      = 1                 # top band
    m["right"][h-th:, :]    = 1                 # bottom band
    m["front"][:, w-tw:]    = 1                 # right band
    m["back"] [:, :tw]      = 1                 # left band
    return m

# ---------- 5) main ----------
def extract_regions_with_x(pdf_path, page_num=0, x_score_thr=0.45):
    crop = render_and_crop(pdf_path, page_num)
    boxes, bw = find_seat_squares(crop)
    masks = region_masks(bw.shape)

    out = {k: False for k in ["front","back","left","right"]}
    scores = {k: 0.0 for k in ["front","back","left","right"]}

    for (x,y,w,h) in boxes:
        roi = bw[y:y+h, x:x+w]
        ok, sc = has_x(roi, score_thr=x_score_thr)
        if not ok: continue
        cx, cy = x + w//2, y + h//2
        for k, M in masks.items():
            if M[cy, cx]:
                out[k] = True
                scores[k] = max(scores[k], sc)

    # Optional: return also square count / best scores for QA
    out.update({f"{k}_score": round(v,3) for k,v in scores.items()})
    out["squares_scanned"] = len(boxes)
    return out

# Example:
back, front, left, right = [], [], [], []
for file in df['filename']: 
    try: 
        print(file)
        res = extract_regions_with_x(file, page_num=0)
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
