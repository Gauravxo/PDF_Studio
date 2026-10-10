# pdf_ops.py — Gauravxo PDF Studio (backend)
import os
import sys
import shutil
import glob
import tempfile
import subprocess
import pikepdf
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


# ============================================================
#  Ghostscript
# ============================================================

def find_ghostscript():
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        for candidate in (
            os.path.join(base, "ghostscript", "bin", "gswin64c.exe"),
            os.path.join(base, "_internal", "ghostscript", "bin", "gswin64c.exe"),
            os.path.join(os.path.dirname(sys.executable), "ghostscript", "bin", "gswin64c.exe"),
        ):
            if os.path.exists(candidate):
                return candidate
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        dev = os.path.join(here, "ghostscript", "bin", "gswin64c.exe")
        if os.path.exists(dev):
            return dev

    for exe in ("gswin64c", "gswin32c", "gs"):
        p = shutil.which(exe)
        if p:
            return p

    gs_root = r"C:\Program Files\gs"
    if os.path.isdir(gs_root):
        for folder in sorted(os.listdir(gs_root), reverse=True):
            exe = os.path.join(gs_root, folder, "bin", "gswin64c.exe")
            if os.path.exists(exe):
                return exe
    return None


def _setup_gs_env():
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        roots = [
            os.path.join(base, "ghostscript"),
            os.path.join(base, "_internal", "ghostscript"),
            os.path.join(os.path.dirname(sys.executable), "ghostscript"),
        ]
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        roots = [os.path.join(here, "ghostscript")]

    for root in roots:
        if os.path.isdir(root):
            os.environ["GS_LIB"] = os.pathsep.join([
                os.path.join(root, "lib"),
                os.path.join(root, "Resource", "Init"),
                os.path.join(root, "Resource", "Font"),
            ])
            return


_setup_gs_env()


def _run_gs(args):
    gs = find_ghostscript()
    if not gs:
        raise RuntimeError("Ghostscript was not found. Reinstall Gauravxo PDF Studio.")
    subprocess.run([gs] + args, check=True, creationflags=_NO_WINDOW)


# ============================================================
#  PDF Compression — Powerful & Customizable
# ============================================================

def _gs_compress_once(gs_path, input_path, output_path, quality, dpi):
    """Run one Ghostscript compression pass with custom quality + DPI."""
    cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        "-dSAFER",
        # Color image downsampling
        "-dDownsampleColorImages=true",
        f"-dColorImageResolution={int(dpi)}",
        "-dColorImageDownsampleType=/Bicubic",
        "-dColorImageDownsampleThreshold=1.0",
        # Gray image downsampling
        "-dDownsampleGrayImages=true",
        f"-dGrayImageResolution={int(dpi)}",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dGrayImageDownsampleThreshold=1.0",
        # Mono image downsampling
        "-dDownsampleMonoImages=true",
        f"-dMonoImageResolution={int(dpi)}",
        "-dMonoImageDownsampleType=/Subsample",
        "-dMonoImageDownsampleThreshold=1.0",
        # Force JPEG re-encoding
        "-dAutoFilterColorImages=false",
        "-dAutoFilterGrayImages=false",
        "-dColorImageFilter=/DCTEncode",
        "-dGrayImageFilter=/DCTEncode",
        f"-dJPEGQ={int(quality)}",
        # Font & duplicate optimization
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dEmbedAllFonts=true",
        "-dDetectDuplicateImages=true",
        "-dCompressPages=true",
        # Strip metadata
        "-dPreserveMarkedContent=false",
        # Output
        f"-sOutputFile={output_path}",
        input_path,
    ]
    subprocess.run(cmd, check=True, creationflags=_NO_WINDOW)


def compress_pdf(input_path, output_path, quality=75, dpi=150,
                 target_size_mb=None, log_callback=None):
    """
    Compress a PDF.

    Args:
        input_path: Source PDF
        output_path: Destination PDF
        quality: JPEG quality 1-100 (only used when target_size_mb is None)
        dpi: Target image DPI (only used when target_size_mb is None)
        target_size_mb: Optional desired file size in MB. If set, the tool
                        searches for the best quality/DPI combo to hit it.
        log_callback: Optional function(msg) to receive progress updates.
    """
    def _log(msg):
        if log_callback:
            try:
                log_callback(msg)
            except Exception:
                pass

    gs = find_ghostscript()
    if not gs:
        raise RuntimeError("Ghostscript was not found. Reinstall Gauravxo PDF Studio.")

    input_size = os.path.getsize(input_path)

    # ---- Manual mode ----
    if target_size_mb is None:
        _log(f"Compressing with quality={quality}, dpi={dpi}...")
        _gs_compress_once(gs, input_path, output_path, quality, dpi)
        out_size = os.path.getsize(output_path)
        pct = (1 - out_size / input_size) * 100 if input_size else 0
        _log(f"Before: {input_size / 1024 / 1024:.2f} MB")
        _log(f"After:  {out_size / 1024 / 1024:.2f} MB")
        _log(f"Saved:  {pct:.1f}%")
        return

    # ---- Target size mode ----
    target_bytes = target_size_mb * 1024 * 1024
    _log(f"Target: {target_size_mb:.2f} MB (current: {input_size / 1024 / 1024:.2f} MB)")

    if input_size <= target_bytes:
        shutil.copy2(input_path, output_path)
        _log("File is already smaller than target. Copied unchanged.")
        return

    # Try from highest quality → lowest, stop at first fit
    attempts = [
        (95, 300), (90, 250), (85, 200),
        (75, 150), (65, 130), (55, 110),
        (45, 90),  (35, 75),  (25, 60),
        (15, 50),  (10, 40),  (5, 30),
    ]

    temp_dir = tempfile.mkdtemp(prefix="pdfcomp_")
    best_under = None       # first path that meets target
    smallest_over = None    # smallest we found even if > target
    smallest_size = None

    try:
        for q, d in attempts:
            temp_path = os.path.join(temp_dir, f"try_q{q}_d{d}.pdf")
            try:
                _gs_compress_once(gs, input_path, temp_path, q, d)
                size = os.path.getsize(temp_path)
                _log(f"  Try q={q}, dpi={d} → {size / 1024 / 1024:.2f} MB")

                if size <= target_bytes:
                    best_under = temp_path
                    break
                else:
                    if smallest_size is None or size < smallest_size:
                        if smallest_over and os.path.exists(smallest_over):
                            try:
                                os.remove(smallest_over)
                            except OSError:
                                pass
                        smallest_over = temp_path
                        smallest_size = size
                    else:
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass
            except Exception as e:
                _log(f"  Try q={q}, dpi={d} failed: {e}")
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

        chosen = best_under or smallest_over
        if chosen and os.path.exists(chosen):
            shutil.move(chosen, output_path)
            out_size = os.path.getsize(output_path)
            pct = (1 - out_size / input_size) * 100 if input_size else 0
            _log(f"Final:  {out_size / 1024 / 1024:.2f} MB (saved {pct:.1f}%)")
            if best_under:
                _log("✓ Target size achieved.")
            else:
                _log("⚠ Could not reach target — using smallest result.")
        else:
            raise RuntimeError("Compression produced no output.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================
#  Merge / Split
# ============================================================

def merge_pdfs(paths, output_path):
    with pikepdf.Pdf.new() as out:
        for p in paths:
            with pikepdf.open(p) as pdf:
                out.pages.extend(pdf.pages)
        out.save(output_path)


def parse_ranges(range_str, total_pages):
    if range_str.strip().lower() == "all":
        return list(range(total_pages))
    pages = set()
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            s, e = part.split("-", 1)
            s, e = int(s.strip()), int(e.strip())
            for i in range(s, e + 1):
                if 1 <= i <= total_pages:
                    pages.add(i - 1)
        else:
            i = int(part)
            if 1 <= i <= total_pages:
                pages.add(i - 1)
    return sorted(pages)


def split_pdf(input_path, output_dir, mode="each", ranges=None):
    os.makedirs(output_dir, exist_ok=True)
    with pikepdf.open(input_path) as pdf:
        total = len(pdf.pages)
        if mode == "each":
            for i in range(total):
                out = pikepdf.Pdf.new()
                out.pages.append(pdf.pages[i])
                out.save(os.path.join(output_dir, f"page_{i + 1:03d}.pdf"))
        elif mode == "ranges" and ranges:
            for idx, (s, e) in enumerate(ranges, 1):
                out = pikepdf.Pdf.new()
                for i in range(s - 1, min(e, total)):
                    out.pages.append(pdf.pages[i])
                out.save(os.path.join(output_dir, f"split_{idx}_{s}-{e}.pdf"))


# ============================================================
#  Images <-> PDF
# ============================================================

def images_to_pdf(image_paths, output_path, page_size="A4", margin=0):
    imgs = []
    for p in image_paths:
        img = Image.open(p)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        imgs.append(img)
    if not imgs:
        return

    if page_size == "Fit":
        imgs[0].save(output_path, save_all=True,
                     append_images=imgs[1:], resolution=100.0)
        return

    sizes = {"A4": (595, 842), "Letter": (612, 792), "Legal": (612, 1008)}
    pw, ph = sizes.get(page_size, (595, 842))

    pages = []
    for img in imgs:
        max_w, max_h = pw - 2 * margin, ph - 2 * margin
        ratio = min(max_w / img.width, max_h / img.height)
        new_w, new_h = max(1, int(img.width * ratio)), max(1, int(img.height * ratio))
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (pw, ph), "white")
        canvas.paste(resized, ((pw - new_w) // 2, (ph - new_h) // 2))
        pages.append(canvas)

    pages[0].save(output_path, save_all=True,
                  append_images=pages[1:], resolution=72.0)


def pdf_to_images(input_path, output_dir, fmt="PNG", dpi=150):
    os.makedirs(output_dir, exist_ok=True)
    device = "png16m" if fmt.upper() == "PNG" else "jpeg"
    out_pattern = os.path.join(output_dir, f"page_%03d.{fmt.lower()}")
    _run_gs([
        f"-sDEVICE={device}",
        f"-r{dpi}",
        "-dNOPAUSE", "-dBATCH", "-dQUIET",
        f"-sOutputFile={out_pattern}",
        input_path,
    ])


# ============================================================
#  Page operations
# ============================================================

def rotate_pdf(input_path, output_path, angle, pages="all"):
    with pikepdf.open(input_path) as pdf:
        total = len(pdf.pages)
        idxs = parse_ranges(pages, total) if pages != "all" else range(total)
        for i in idxs:
            page = pdf.pages[i]
            page.Rotate = (int(page.get("/Rotate", 0)) + angle) % 360
        pdf.save(output_path)


def delete_pages(input_path, output_path, pages):
    with pikepdf.open(input_path) as pdf:
        total = len(pdf.pages)
        to_del = set(parse_ranges(pages, total))
        out = pikepdf.Pdf.new()
        for i in range(total):
            if i not in to_del:
                out.pages.append(pdf.pages[i])
        out.save(output_path)


def extract_pages(input_path, output_path, pages):
    with pikepdf.open(input_path) as pdf:
        total = len(pdf.pages)
        out = pikepdf.Pdf.new()
        for i in parse_ranges(pages, total):
            out.pages.append(pdf.pages[i])
        out.save(output_path)


# ============================================================
#  Protect / Unlock
# ============================================================

def protect_pdf(input_path, output_path, password):
    with pikepdf.open(input_path) as pdf:
        pdf.save(output_path, encryption=pikepdf.Encryption(
            owner=password, user=password, R=6))


def unlock_pdf(input_path, output_path, password):
    with pikepdf.open(input_path, password=password) as pdf:
        pdf.save(output_path)


# ============================================================
#  Image Size Reducer
# ============================================================

def reduce_image_size(input_paths, output_dir, quality=75,
                      max_dim=0, out_format="Auto", suffix="_reduced"):
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for path in input_paths:
        try:
            src_size = os.path.getsize(path)
            img = Image.open(path)
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            fmt = out_format
            if fmt == "Auto":
                src_fmt = (img.format or "JPEG").upper()
                fmt = "JPEG" if src_fmt == "JPEG" else ("WEBP" if src_fmt == "WEBP" else "PNG")

            if fmt == "JPEG":
                if img.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    rgba = img.convert("RGBA")
                    bg.paste(rgba, mask=rgba.split()[-1])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")
            elif fmt == "WEBP":
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")

            if max_dim and max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                img = img.resize(
                    (max(1, int(img.width * ratio)), max(1, int(img.height * ratio))),
                    Image.LANCZOS,
                )

            base = os.path.splitext(os.path.basename(path))[0]
            ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[fmt]
            out_path = os.path.join(output_dir, f"{base}{suffix}{ext}")

            kw = {}
            if fmt == "JPEG":
                kw = dict(quality=quality, optimize=True, progressive=True)
            elif fmt == "PNG":
                kw = dict(optimize=True, compress_level=9)
            elif fmt == "WEBP":
                kw = dict(quality=quality, method=6)

            img.save(out_path, fmt, **kw)
            results.append((path, out_path, src_size, os.path.getsize(out_path)))
        except Exception as e:
            results.append((path, None,
                            os.path.getsize(path) if os.path.exists(path) else 0, 0))
            print(f"[reduce_image_size] {path}: {e}")

    return results


# ============================================================
#  OCR  (tesseract.exe direct, with strong preprocessing)
# ============================================================

def find_tesseract():
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        for candidate in (
            os.path.join(base, "Tesseract-OCR", "tesseract.exe"),
            os.path.join(base, "_internal", "Tesseract-OCR", "tesseract.exe"),
            os.path.join(os.path.dirname(sys.executable), "Tesseract-OCR", "tesseract.exe"),
        ):
            if os.path.exists(candidate):
                return candidate
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        dev = os.path.join(here, "Tesseract-OCR", "tesseract.exe")
        if os.path.exists(dev):
            return dev

    p = shutil.which("tesseract")
    if p:
        return p

    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def find_tessdata(tess_exe):
    root = os.path.dirname(tess_exe)
    for c in (
        os.path.join(root, "tessdata"),
        os.path.join(os.path.dirname(root), "tessdata"),
        root,
    ):
        if os.path.exists(os.path.join(c, "eng.traineddata")):
            return c
    return None


def _preprocess_for_ocr(image_path, max_dim=3500):
    img = Image.open(image_path)

    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    longest = max(w, h)
    if longest > max_dim:
        ratio = max_dim / longest
        img = img.resize((max(1, int(w * ratio)), max(1, int(h * ratio))),
                         Image.LANCZOS)
    elif longest < 1500:
        ratio = 1500 / longest
        img = img.resize((max(1, int(w * ratio)), max(1, int(h * ratio))),
                         Image.LANCZOS)

    img = img.convert("L")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(1.8)

    pixels = list(img.getdata())
    mean = sum(pixels) / len(pixels) if pixels else 128
    if mean < 110:
        img = ImageOps.invert(img)

    img = img.point(lambda p: 255 if p > 160 else 0, mode="1").convert("L")

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    img.save(tmp.name, "PNG")
    return tmp.name


def _tesseract_run(tess_exe, image_path, lang="eng", psm=3, oem=3):
    tessdata = find_tessdata(tess_exe)
    if not tessdata:
        raise RuntimeError("Tessdata folder not found next to tesseract.exe.")

    clean = _preprocess_for_ocr(image_path)

    cmd = [
        tess_exe,
        clean,
        "stdout",
        "-l", lang,
        "--tessdata-dir", tessdata,
        "--dpi", "300",
        "--oem", str(oem),
        "--psm", str(psm),
        "-c", "preserve_interword_spaces=1",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            creationflags=_NO_WINDOW,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Tesseract took too long (>3 min). Try a smaller image.")
    finally:
        try:
            os.remove(clean)
        except OSError:
            pass

    if result.returncode != 0:
        raise RuntimeError(
            f"Tesseract failed (exit {result.returncode}).\n\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )
    return result.stdout


def ocr_images_to_text(image_paths, output_dir, lang="eng", psm=3, suffix="_ocr"):
    tess_exe = find_tesseract()
    if not tess_exe:
        raise RuntimeError("Tesseract OCR was not found. Reinstall the app.")
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for path in image_paths:
        text = _tesseract_run(tess_exe, path, lang=lang, psm=psm)
        base = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(output_dir, f"{base}{suffix}.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        results.append((path, out))
    return results


def ocr_pdf_to_text(input_pdf, output_txt, dpi=300, lang="eng", psm=3):
    tess_exe = find_tesseract()
    if not tess_exe:
        raise RuntimeError("Tesseract OCR was not found. Reinstall the app.")

    with tempfile.TemporaryDirectory() as tmp:
        pdf_to_images(input_pdf, tmp, fmt="PNG", dpi=dpi)
        pages = sorted(glob.glob(os.path.join(tmp, "page_*.png")))
        if not pages:
            raise RuntimeError("No pages were rendered from the PDF.")
        chunks = []
        total = len(pages)
        for i, png in enumerate(pages, 1):
            text = _tesseract_run(tess_exe, png, lang=lang, psm=psm)
            chunks.append(f"===== Page {i} of {total} =====\n{text}\n")
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(chunks))
    return output_txt