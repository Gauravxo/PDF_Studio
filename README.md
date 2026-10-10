<div align="center">

# 🎨 Gaurav.xo PDF Studio

### Offline PDF & Image Toolkit — 13 Tools, Zero Internet, Zero Install

[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Gauravxo)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.12-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-Personal%20Use-ff69b4?style=for-the-badge)](LICENSE)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red?style=for-the-badge)](https://gauravxo.github.io/)

**A free, modern, fully offline PDF & image toolkit for Windows.**  
No uploads. No accounts. No tracking. Just powerful tools that run 100% on your PC.

[Features](#-features) · [Screenshots](#-screenshots) · [Download](#-download) · [Tech Stack](#-tech-stack) · [My Story](#-my-story) · [License](#-license)

</div>

---

## ✨ Features

Gaurav.xo PDF Studio bundles **13 powerful tools** into one clean, modern desktop app:

| # | Tool | Description |
|---|------|-------------|
| 1 | 📉 **Compress PDF** | Reduce PDF size with manual quality/DPI sliders **or** target a specific file size (auto-search mode). Huge savings on scanned/photo PDFs. |
| 2 | 🔗 **Merge PDF** | Combine multiple PDFs in any order with drag & drop. |
| 3 | ✂️ **Split PDF** | Split by every page or custom ranges (`1-3,5-7`). |
| 4 | 🖼️ **Images → PDF** | Batch convert JPG/PNG/WEBP/BMP/TIFF to A4/Letter/Legal/Fit PDFs with custom margins. |
| 5 | 📸 **PDF → Images** | Export PDF pages as PNG or JPG at any DPI (72–600). |
| 6 | 🔄 **Rotate** | Rotate pages 90° / 180° / 270° — all pages or any range. |
| 7 | 🗑️ **Delete Pages** | Remove specific pages from a PDF. |
| 8 | 📤 **Extract Pages** | Pull specific pages into a new PDF. |
| 9 | 🔒 **Protect PDF** | Encrypt your PDF with a password. |
| 10 | 🔓 **Unlock PDF** | Remove a known password from a PDF. |
| 11 | 🎚️ **Image Size Reducer** | Batch-shrink images with quality slider + optional resize. |
| 12 | 🔍 **OCR / Text Extractor** | Extract text from images or scanned PDFs — 11 languages supported (English, Hindi, French, German, Spanish, Chinese, Arabic, and more). |
| 13 | ℹ️ **About** | Clean info page with author links. |

---

## 🎯 Highlights

- 🔌 **100% Offline** — never connects to the internet
- 📦 **No Install Needed** — runs from a USB stick (portable build)
- 🪄 **No Python Required** — everything is bundled in one .exe
- ⚡ **Instant Launch** — native Windows performance via PySide6 (Qt 6)
- 🎨 **Modern UI** — clean Fusion theme, drag & drop everywhere
- 🌍 **Multi-Language OCR** — Tesseract 5 with 11 trained languages
- 🧵 **Threaded Operations** — UI never freezes on large files
- 📊 **Live Progress + Logs** — every tool shows real-time status

---

## 📸 Screenshots

> _Screenshots coming soon — but trust me, it looks great._

| Compress PDF | Merge PDF | OCR |
|---|---|---|
| _screenshot_ | _screenshot_ | _screenshot_ |

*(Replace `_screenshot_` with actual images uploaded to the `/screenshots/` folder of this repo.)*

---

## 📥 Download

Grab the latest release from the **[Releases page](https://github.com/Gauravxo/GauravxoPDFStudio/releases)**.

Two versions available:

### 🎒 Portable (recommended for USB / no-install)
`GauravxoPDFStudio_Portable.zip` — **~200 MB**
1. Download the ZIP
2. Extract anywhere (Desktop, USB, D:\)
3. Double-click `GauravxoPDFStudio.exe`
4. Done — no install, no admin rights, no internet

### 💾 Installer (for regular use)
`GauravxoPDFStudio_Setup.exe` — **~120 MB**
1. Download the `.exe`
2. Double-click → Next → Install → Finish
3. Launch from Start Menu

> **⚠️ Windows SmartScreen may warn "Unknown Publisher"** on first launch — click **More info → Run anyway**. This is normal for unsigned software.

---

## 🖥️ System Requirements

| Requirement | Minimum |
|---|---|
| OS | Windows 10 (build 1903+) or Windows 11 |
| Architecture | 64-bit (x64) |
| RAM | 4 GB (8 GB recommended for large PDFs) |
| Disk | 400 MB |
| Internet | ❌ Not required after download |

---

## 🛠️ Tech Stack

Built from scratch with a focus on reliability and privacy:

- **[Python 3.12](https://python.org)** — core language
- **[PySide6 (Qt 6)](https://pypi.org/project/PySide6/)** — GUI framework
- **[Ghostscript 10.08](https://ghostscript.com/)** — PDF compression + rasterization engine (bundled)
- **[pikepdf](https://pikepdf.readthedocs.io/)** — lossless PDF manipulation (merge, split, rotate, encrypt)
- **[Pillow](https://pillow.readthedocs.io/)** — image processing
- **[Tesseract OCR 5](https://github.com/tesseract-ocr/tesseract)** — offline text extraction (bundled)
- **[PyInstaller](https://pyinstaller.org/)** — packaging into standalone Windows exe
- **[Inno Setup](https://jrsoftware.org/isinfo.php)** — installer creation

---

## 🚀 How It Works (Under the Hood)

```
┌─────────────────────────────────────────────────────┐
│              Gaurav.xo PDF Studio                   │
├─────────────────────────────────────────────────────┤
│  GUI Layer (PySide6 / Qt 6)                         │
│    ├── 13 tab-based tools                           │
│    ├── Drag & drop file handling                    │
│    └── QThread workers (non-blocking UI)            │
├─────────────────────────────────────────────────────┤
│  Backend Layer (pdf_ops.py)                         │
│    ├── Ghostscript subprocess calls                 │
│    ├── pikepdf PDF manipulation                     │
│    ├── Pillow image processing                      │
│    └── Tesseract OCR via subprocess                 │
├─────────────────────────────────────────────────────┤
│  Bundled Dependencies                               │
│    ├── ghostscript/  → GS 10.08 (portable)          │
│    ├── Tesseract-OCR/ → OCR engine + languages      │
│    └── _internal/    → Python runtime + libraries   │
└─────────────────────────────────────────────────────┘
```

**Smart compression strategy:**
- Manual mode → passes quality + DPI directly to Ghostscript's `-dJPEGQ` and `-dColorImageResolution`
- Target size mode → iteratively tries 12 quality/DPI combos, stops when the target is met (within 5%)

---

## 💡 My Story — Why I Built This

I got tired of online PDF tools.

Every one I tried wanted me to **upload my private documents to their server**, show me ads, cap my file size at 5 MB, or charge me a subscription for basic features.

One day I needed to compress a **personal, sensitive PDF** — and I realized every "free" online option was asking me to hand over my data to strangers. That didn't sit right.

So I decided: **I'll build my own.** One that runs **completely offline**, keeps my files **only on my PC**, and does everything I need — compress, merge, split, convert, protect, OCR — all in one place.

### The Struggles (yes, there were many)

Building this wasn't smooth. Let me be honest:

- 🔴 **Ghostscript integration nearly broke me** — the "portable" ZIP I downloaded first was Ghost**XPS**, not Ghostscript. Spent hours debugging why compression silently failed.
- 🔴 **Bundling 200 MB of dependencies into one exe** with PyInstaller — took me 20+ tries to figure out `--add-data` and `--onedir` vs `--onefile`.
- 🔴 **"Failed to load Python DLL"** — first test on a friend's PC failed spectacularly. Turned out I was shipping the wrong folder structure.
- 🔴 **The compressor barely worked at first** — 3.88 MB → 3.75 MB on "maximum" settings. Turned out Ghostscript's built-in presets (`/screen`, `/ebook`) are too conservative. I had to bypass them and take direct control of JPEG quality + image DPI, then add an iterative search loop to hit user-defined target sizes.
- 🔴 **OCR was a nightmare** — Tesseract refused to bundle properly, then tessdata was missing, then images needed preprocessing (grayscale + denoise + binarize + invert) before it would read anything useful. Took a week of trial and error.
- 🔴 **SmartScreen warnings scared my first testers** — spent hours explaining that an unsigned exe is not a virus.

### But it was worth it

After **weeks of iteration**, I ended up with:

- ✅ A working app with **13 tools**
- ✅ **200 MB portable ZIP** that runs on any Windows 10/11 PC with **zero installs**
- ✅ Real **PDF compression** (up to 90% reduction on scanned documents)
- ✅ **Offline OCR** in 11 languages
- ✅ **A tool I actually use daily** — and now my friends and family do too

This isn't a product. It's a solution I built for myself, and I'm sharing it because I know others are tired of the same online-tool nonsense.

If it saves you time, a ⭐ on this repo makes my day.

---

## 🔧 Building It Yourself

Want to compile it on your own machine? Here's how:

### Prerequisites
- Python 3.12
- Windows 10/11 (64-bit)
- [Ghostscript 10.x](https://www.ghostscript.com/releases/gsdnld.html) (portable ZIP extracted to `ghostscript/`)
- [Tesseract 5](https://github.com/UB-Mannheim/tesseract/wiki) (portable folder `Tesseract-OCR/`)
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (optional, for installer)

### Build commands

```powershell
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Run from source
python main.py

# 3. Build portable
pyinstaller --noconsole --onedir --name GauravxoPDFStudio `
  --icon icon.ico `
  --add-data "ghostscript;ghostscript" `
  --add-data "Tesseract-OCR;Tesseract-OCR" `
  main.py

# 4. Package
Compress-Archive -Path "dist\GauravxoPDFStudio\*" `
  -DestinationPath "GauravxoPDFStudio_Portable.zip" -Force
```

---

## 🗺️ Roadmap

Ideas for future versions:

- [ ] 🎨 **Dark mode / theme switcher**
- [ ] 🔐 **PDF redaction** (permanently black out text)
- [ ] 🧾 **PDF/A archival format** conversion
- [ ] 💧 **Watermark** and **page numbers**
- [ ] 🖱️ **Right-click shell integration** ("Compress with Gaurav.xo PDF Studio")
- [ ] 📝 **PDF metadata editor** (title, author, keywords)
- [ ] 🖨️ **Batch processing** (multiple PDFs at once)

Have an idea? [Open an issue](https://github.com/Gauravxo/GauravxoPDFStudio/issues) 🎯

---

## 🤝 Contributing

This is a personal project, but I welcome:

- 🐛 **Bug reports** — [open an issue](https://github.com/Gauravxo/GauravxoPDFStudio/issues)
- 💡 **Feature suggestions** — I'll consider anything reasonable
- 🌍 **Translation help** — for the UI or for additional OCR languages
- ⭐ **A star** if it made your life easier

---

## 📜 License

This project is released for **personal and non-commercial use**.

**Bundled software:**
- **Ghostscript** — [AGPL License](https://www.ghostscript.com/licensing/index.html). For commercial distribution, you must either open-source under AGPL or purchase a commercial license from Artifex.
- **Tesseract OCR** — [Apache 2.0 License](https://github.com/tesseract-ocr/tesseract/blob/main/LICENSE)
- **PySide6 / Qt 6** — [LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.html)
- **pikepdf** — [MPL 2.0](https://www.mozilla.org/en-US/MPL/2.0/)
- **Pillow** — [HPND License](https://github.com/python-pillow/Pillow/blob/main/LICENSE)

If you plan to **sell** or **commercially distribute** this app, please read Ghostscript's license first.

---

## 🙏 Acknowledgements

- Thanks to the **Ghostscript team** for a rock-solid PDF engine
- Thanks to **Tesseract OCR** maintainers
- Thanks to the **PySide6 / Qt** community
- And thanks to everyone who tested early builds and reported bugs — you made this better

---

## 👤 Author

**Gaurav.xo**

[![Website](https://img.shields.io/badge/Website-gauravxo.github.io-FF6B6B?style=flat-square&logo=googlechrome&logoColor=white)](https://gauravxo.github.io/)
[![GitHub](https://img.shields.io/badge/GitHub-Gauravxo-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Gauravxo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-gauravxo-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gauravxo/)

---

<div align="center">

### ⭐ If this helped you, star the repo — it means a lot.

**Made with ❤️ and a lot of ☕ by Gaurav.xo**

</div>