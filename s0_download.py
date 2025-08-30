# pip install requests beautifulsoup4
import os, re, sys, pathlib, urllib.parse, requests, math
from bs4 import BeautifulSoup

BASE_URL = "https://www.dmv.ca.gov/portal/vehicle-industry-services/autonomous-vehicles/autonomous-vehicle-collision-reports/"
OUT_DIR = pathlib.Path("dmv_av_collision_reports"); OUT_DIR.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}

def human_size(n):
    if n is None: return "unknown"
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024: return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

def get_soup(url):
    print(f"[1/4] Fetching page: {url}")
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    print(f"      OK ({len(r.text):,} chars). Parsing HTML…")
    return BeautifulSoup(r.text, "html.parser")

def candidate_links(soup):
    # Yield possible PDF links; DMV uses /portal/file/... redirects
    for a in soup.find_all("a", href=True):
        text = (a.get_text() or "").strip()
        href = a["href"].strip()
        if "(PDF)" in text or "/portal/file/" in href or href.lower().endswith(".pdf"):
            yield urllib.parse.urljoin(BASE_URL, href)

def resolve_pdf(url, idx=None, total=None):
    tag = f"[{idx}/{total}] " if (idx and total) else ""
    try:
        print(f"    {tag}HEAD -> {url}")
        h = requests.head(url, headers=UA, allow_redirects=True, timeout=60)
        print(f"         status={h.status_code}, final={h.url}")
        if h.status_code >= 400:
            print("         skip (HTTP error)")
            return None, None
        ctype = (h.headers.get("Content-Type") or "").lower()
        final = h.url
        if "application/pdf" in ctype or final.lower().endswith(".pdf"):
            cd = h.headers.get("Content-Disposition", "")
            m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
            if m:
                fname = urllib.parse.unquote(m.group(1))
            else:
                fname = pathlib.Path(urllib.parse.urlparse(final).path).name or "file.pdf"
            print(f"         ✓ PDF detected -> {fname}")
            return final, fname
        print("         skip (not a PDF)")
        return None, None
    except requests.RequestException as e:
        print(f"         skip (HEAD error: {e})")
        return None, None

def download(url, dest_name):
    dest = OUT_DIR / dest_name
    if dest.exists():
        print(f"    download: skip (exists): {dest_name}")
        return
    print(f"    download: GET -> {url}")
    with requests.get(url, headers=UA, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = r.headers.get("Content-Length")
        total_int = int(total) if total and total.isdigit() else None
        print(f"        saving as: {dest_name} (size: {human_size(total_int)})")
        bytes_written = 0
        chunk = 1 << 15  # 32 KiB
        with open(dest, "wb") as f:
            for i, part in enumerate(r.iter_content(chunk)):
                if part:
                    f.write(part)
                    bytes_written += len(part)
                    # Print progress every ~2 MB or on completion
                    if (i % (max(1, (2 * 1024 * 1024) // chunk)) == 0) or (total_int and bytes_written >= total_int):
                        if total_int:
                            pct = (bytes_written / total_int) * 100
                            sys.stdout.write(f"\r        progress: {human_size(bytes_written)} / {human_size(total_int)} ({pct:.1f}%)")
                        else:
                            sys.stdout.write(f"\r        progress: {human_size(bytes_written)}")
                        sys.stdout.flush()
        sys.stdout.write("\n")
    print(f"        ✓ saved: {dest_name}")

def main():
    soup = get_soup(BASE_URL)

    print("[2/4] Scanning for candidate links…")
    cand = list(candidate_links(soup))
    print(f"      found {len(cand)} candidate link(s) to inspect")

    print("[3/4] Resolving which candidates are actual PDFs…")
    seen = set()
    pdfs = []
    total = len(cand)
    for i, url in enumerate(cand, 1):
        final, fname = resolve_pdf(url, idx=i, total=total)
        if final and final not in seen:
            seen.add(final)
            pdfs.append((final, fname))
    print(f"      ✓ {len(pdfs)} unique PDF(s) identified")

    print("[4/4] Downloading PDFs…")
    for final, fname in pdfs:
        download(final, fname)

    print("Done.")

if __name__ == "__main__":
    main()
