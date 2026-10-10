# main.py — Gauravxo PDF Studio (GUI)
import os
import sys
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, QTextEdit,
    QProgressBar, QMessageBox, QTabWidget, QRadioButton, QButtonGroup,
    QFileDialog, QAbstractItemView, QSpinBox, QSlider, QGroupBox,
    QDoubleSpinBox, QCheckBox,
)
import pdf_ops

APP_NAME = "Gaurav.xo PDF Studio"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Gaurav.xo"
APP_WEBSITE = "https://gauravxo.github.io/"
APP_GITHUB = "https://github.com/Gauravxo?tab=repositories"
APP_LINKEDIN = "https://www.linkedin.com/in/gauravxo/?isSelfProfile=true"


# ---------------- Worker thread ----------------

class Worker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func, self.args, self.kwargs = func, args, kwargs

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# ---------------- Draggable file list ----------------

class FileListWidget(QListWidget):
    def __init__(self, file_filter=None, parent=None):
        super().__init__(parent)
        self.file_filter = file_filter or (lambda p: True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and self.file_filter(path):
                    self.addItem(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def add_paths(self, paths):
        for p in paths:
            self.addItem(p)

    def paths(self):
        return [self.item(i).text() for i in range(self.count())]

    def remove_selected(self):
        for it in self.selectedItems():
            self.takeItem(self.row(it))

    def move_up(self):
        r = self.currentRow()
        if r > 0:
            it = self.takeItem(r)
            self.insertItem(r - 1, it)
            self.setCurrentRow(r - 1)

    def move_down(self):
        r = self.currentRow()
        if r < self.count() - 1:
            it = self.takeItem(r)
            self.insertItem(r + 1, it)
            self.setCurrentRow(r + 1)


# ---------------- Base tab ----------------

class ToolTab(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.worker = None

    def add_progress_and_log(self):
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        self.main_layout.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(140)
        self.main_layout.addWidget(self.log)

    def start_worker(self, func, *args, **kwargs):
        self.progress.show()
        self.run_btn.setEnabled(False)
        self.log.clear()
        self.worker = Worker(func, *args, **kwargs)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self._on_err)
        self.worker.start()

    def _on_done(self):
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.log.append("✅ Done")
        QMessageBox.information(self, "Success", "Operation completed successfully.")

    def _on_err(self, msg):
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.log.append(f"❌ {msg}")
        QMessageBox.critical(self, "Error", msg)


def _file_row(parent_layout, label, filter_str, is_save=False, default_name=""):
    row = QHBoxLayout()
    row.addWidget(QLabel(label))
    edit = QLineEdit()
    edit.setPlaceholderText("Select file..." if not is_save else "Choose output...")
    row.addWidget(edit)
    btn = QPushButton("Browse")

    if is_save:
        def browse():
            p, _ = QFileDialog.getSaveFileName(parent_layout.parentWidget(),
                                               "Save", default_name, filter_str)
            if p:
                edit.setText(p)
    else:
        def browse():
            p, _ = QFileDialog.getOpenFileName(parent_layout.parentWidget(),
                                               "Open", "", filter_str)
            if p:
                edit.setText(p)

    btn.clicked.connect(browse)
    row.addWidget(btn)
    parent_layout.addLayout(row)
    return edit, btn


# ---------------- Compress ----------------

class CompressTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.input_edit, _ = _file_row(self.main_layout, "Input PDF:", "PDF Files (*.pdf)")

        # --- Manual settings group ---
        self.manual_group = QGroupBox("Manual Compression Settings")
        ml = QVBoxLayout(self.manual_group)

        qrow = QHBoxLayout()
        qrow.addWidget(QLabel("Image Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(70)
        self.quality_val = QLabel("70")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_val.setText(str(v))
        )
        qrow.addWidget(self.quality_slider, 1)
        qrow.addWidget(self.quality_val)
        ml.addLayout(qrow)

        qhint = QLabel("Lower = smaller file, worse image quality")
        qhint.setStyleSheet("color:#888; font-size: 10px;")
        ml.addWidget(qhint)

        drow = QHBoxLayout()
        drow.addWidget(QLabel("Image DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(30, 600)
        self.dpi_spin.setValue(120)
        self.dpi_spin.setSuffix(" dpi")
        drow.addWidget(self.dpi_spin)
        drow.addStretch()
        ml.addLayout(drow)

        dhint = QLabel("72–100 = very small, 150 = balanced, 300 = print quality")
        dhint.setStyleSheet("color:#888; font-size: 10px;")
        ml.addWidget(dhint)

        self.main_layout.addWidget(self.manual_group)

        # --- Target size group ---
        self.target_group = QGroupBox("Target File Size (Auto)")
        tl = QVBoxLayout(self.target_group)

        trow = QHBoxLayout()
        self.target_check = QCheckBox("Compress to a specific size:")
        self.target_check.toggled.connect(self._toggle_target)
        trow.addWidget(self.target_check)

        self.target_spin = QDoubleSpinBox()
        self.target_spin.setRange(0.05, 500.0)
        self.target_spin.setValue(1.0)
        self.target_spin.setDecimals(2)
        self.target_spin.setSingleStep(0.25)
        self.target_spin.setSuffix(" MB")
        self.target_spin.setEnabled(False)
        trow.addWidget(self.target_spin)
        trow.addStretch()
        tl.addLayout(trow)

        thint = QLabel("Tool auto-searches quality/DPI to hit this size")
        thint.setStyleSheet("color:#888; font-size: 10px;")
        tl.addWidget(thint)

        self.main_layout.addWidget(self.target_group)

        # --- Output ---
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Output folder:"))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Where to save compressed PDF...")
        row2.addWidget(self.output_edit)
        btn = QPushButton("Browse")
        btn.clicked.connect(self._pick_out)
        row2.addWidget(btn)
        self.main_layout.addLayout(row2)

        self.run_btn = QPushButton("Compress")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _toggle_target(self, checked):
        self.target_spin.setEnabled(checked)
        self.manual_group.setEnabled(not checked)

    def _pick_out(self):
        p = QFileDialog.getExistingDirectory(self, "Output folder")
        if p:
            self.output_edit.setText(p)

    def run(self):
        src = self.input_edit.text().strip()
        out_dir = self.output_edit.text().strip()
        if not src or not os.path.exists(src):
            QMessageBox.warning(self, "Error", "Select a valid PDF."); return
        if not out_dir:
            QMessageBox.warning(self, "Error", "Select an output folder."); return

        base = os.path.splitext(os.path.basename(src))[0]
        out = os.path.join(out_dir, f"{base}_compressed.pdf")

        quality = self.quality_slider.value()
        dpi = self.dpi_spin.value()
        target_mb = self.target_spin.value() if self.target_check.isChecked() else None

        if target_mb is not None:
            self.log.append(f"Target size mode: {target_mb:.2f} MB")
        else:
            self.log.append(f"Manual mode: quality={quality}, dpi={dpi}")

        log_ref = self.log

        def task():
            pdf_ops.compress_pdf(
                src, out,
                quality=quality,
                dpi=dpi,
                target_size_mb=target_mb,
                log_callback=lambda m: log_ref.append(m),
            )

        self.start_worker(task)


# ---------------- Merge ----------------

class MergeTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.main_layout.addWidget(QLabel("Drag PDFs here. Order = merge order."))
        self.list_widget = FileListWidget(lambda p: p.lower().endswith(".pdf"))
        self.main_layout.addWidget(self.list_widget)

        row = QHBoxLayout()
        for t, s in [("Add PDFs", self._add), ("Remove", self.list_widget.remove_selected),
                     ("Clear", self.list_widget.clear), ("Up", self.list_widget.move_up),
                     ("Down", self.list_widget.move_down)]:
            b = QPushButton(t); b.clicked.connect(s); row.addWidget(b)
        self.main_layout.addLayout(row)

        self.output_edit, _ = _file_row(
            self.main_layout, "Output PDF:", "PDF Files (*.pdf)", is_save=True,
            default_name="merged.pdf")

        self.run_btn = QPushButton("Merge")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _add(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Add PDFs", "", "PDF Files (*.pdf)")
        self.list_widget.add_paths(paths)

    def run(self):
        paths = self.list_widget.paths()
        out = self.output_edit.text().strip()
        if len(paths) < 2:
            QMessageBox.warning(self, "Error", "Add at least 2 PDFs."); return
        if not out:
            QMessageBox.warning(self, "Error", "Choose output file."); return
        self.log.append(f"Merging {len(paths)} files → {out}")
        self.start_worker(pdf_ops.merge_pdfs, paths, out)


# ---------------- Split ----------------

class SplitTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.input_edit, _ = _file_row(self.main_layout, "Input PDF:", "PDF Files (*.pdf)")

        self.group = QButtonGroup(self)
        self.rb_each = QRadioButton("Split every page into separate PDFs")
        self.rb_range = QRadioButton("Split by ranges (e.g. 1-3,4-6)")
        self.rb_each.setChecked(True)
        self.group.addButton(self.rb_each)
        self.group.addButton(self.rb_range)
        self.main_layout.addWidget(self.rb_each)
        self.main_layout.addWidget(self.rb_range)

        row = QHBoxLayout()
        row.addWidget(QLabel("Ranges:"))
        self.ranges_edit = QLineEdit()
        self.ranges_edit.setPlaceholderText("e.g. 1-3,5-7")
        self.ranges_edit.setEnabled(False)
        row.addWidget(self.ranges_edit)
        self.main_layout.addLayout(row)
        self.rb_range.toggled.connect(self.ranges_edit.setEnabled)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Output folder:"))
        self.out_edit = QLineEdit()
        row2.addWidget(self.out_edit)
        b = QPushButton("Browse"); b.clicked.connect(self._pick_out)
        row2.addWidget(b)
        self.main_layout.addLayout(row2)

        self.run_btn = QPushButton("Split")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _pick_out(self):
        p = QFileDialog.getExistingDirectory(self, "Output folder")
        if p:
            self.out_edit.setText(p)

    def run(self):
        src = self.input_edit.text().strip()
        out = self.out_edit.text().strip()
        if not src or not os.path.exists(src):
            QMessageBox.warning(self, "Error", "Select valid PDF."); return
        if not out:
            QMessageBox.warning(self, "Error", "Select output folder."); return

        if self.rb_each.isChecked():
            mode, ranges = "each", None
        else:
            mode = "ranges"
            txt = self.ranges_edit.text().strip()
            if not txt:
                QMessageBox.warning(self, "Error", "Enter ranges."); return
            ranges = []
            for part in txt.split(","):
                part = part.strip()
                if not part: continue
                if "-" in part:
                    s, e = part.split("-", 1)
                    ranges.append((int(s), int(e)))
                else:
                    p = int(part); ranges.append((p, p))

        self.log.append(f"Splitting {src} → {out}")
        self.start_worker(pdf_ops.split_pdf, src, out, mode, ranges)


# ---------------- Images → PDF ----------------

class ImagesToPdfTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.main_layout.addWidget(QLabel("Drag images here. Order matters."))
        self.list_widget = FileListWidget(
            lambda p: p.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp")))
        self.main_layout.addWidget(self.list_widget)

        row = QHBoxLayout()
        for t, s in [("Add Images", self._add), ("Remove", self.list_widget.remove_selected),
                     ("Clear", self.list_widget.clear), ("Up", self.list_widget.move_up),
                     ("Down", self.list_widget.move_down)]:
            b = QPushButton(t); b.clicked.connect(s); row.addWidget(b)
        self.main_layout.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Page size:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["A4", "Letter", "Legal", "Fit"])
        row2.addWidget(self.size_combo)
        row2.addWidget(QLabel("Margin:"))
        self.margin_spin = QSpinBox(); self.margin_spin.setRange(0, 100); self.margin_spin.setValue(0)
        self.margin_spin.setSuffix(" pt")
        row2.addWidget(self.margin_spin)
        row2.addStretch()
        self.main_layout.addLayout(row2)

        self.output_edit, _ = _file_row(
            self.main_layout, "Output PDF:", "PDF Files (*.pdf)", is_save=True,
            default_name="images.pdf")

        self.run_btn = QPushButton("Create PDF")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _add(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp)")
        self.list_widget.add_paths(paths)

    def run(self):
        paths = self.list_widget.paths()
        out = self.output_edit.text().strip()
        if not paths:
            QMessageBox.warning(self, "Error", "Add at least one image."); return
        if not out:
            QMessageBox.warning(self, "Error", "Choose output file."); return
        self.log.append(f"Creating PDF from {len(paths)} images.")
        self.start_worker(pdf_ops.images_to_pdf, paths, out,
                          self.size_combo.currentText(), self.margin_spin.value())


# ---------------- PDF → Images ----------------

class PdfToImagesTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.input_edit, _ = _file_row(self.main_layout, "Input PDF:", "PDF Files (*.pdf)")

        row = QHBoxLayout()
        row.addWidget(QLabel("Format:"))
        self.fmt_combo = QComboBox(); self.fmt_combo.addItems(["PNG", "JPG"])
        row.addWidget(self.fmt_combo)
        row.addWidget(QLabel("DPI:"))
        self.dpi_spin = QSpinBox(); self.dpi_spin.setRange(72, 600); self.dpi_spin.setValue(150)
        row.addWidget(self.dpi_spin)
        row.addStretch()
        self.main_layout.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Output folder:"))
        self.out_edit = QLineEdit()
        row2.addWidget(self.out_edit)
        b = QPushButton("Browse"); b.clicked.connect(self._pick_out)
        row2.addWidget(b)
        self.main_layout.addLayout(row2)

        self.run_btn = QPushButton("Convert")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _pick_out(self):
        p = QFileDialog.getExistingDirectory(self, "Output folder")
        if p:
            self.out_edit.setText(p)

    def run(self):
        src = self.input_edit.text().strip()
        out = self.out_edit.text().strip()
        if not src or not os.path.exists(src):
            QMessageBox.warning(self, "Error", "Select valid PDF."); return
        if not out:
            QMessageBox.warning(self, "Error", "Select output folder."); return
        self.log.append(f"Converting {src} → {self.fmt_combo.currentText()}")
        self.start_worker(pdf_ops.pdf_to_images, src, out,
                          self.fmt_combo.currentText(), self.dpi_spin.value())


# ---------------- Rotate ----------------

class RotateTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.input_edit, _ = _file_row(self.main_layout, "Input PDF:", "PDF Files (*.pdf)")

        row = QHBoxLayout()
        row.addWidget(QLabel("Angle:"))
        self.angle_combo = QComboBox(); self.angle_combo.addItems(["90", "180", "270"])
        row.addWidget(self.angle_combo)
        row.addWidget(QLabel("Pages:"))
        self.pages_edit = QLineEdit("all")
        self.pages_edit.setPlaceholderText("all, or 1-3,5")
        row.addWidget(self.pages_edit)
        self.main_layout.addLayout(row)

        self.output_edit, _ = _file_row(
            self.main_layout, "Output PDF:", "PDF Files (*.pdf)", is_save=True)

        self.run_btn = QPushButton("Rotate")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def run(self):
        src = self.input_edit.text().strip()
        out = self.output_edit.text().strip()
        if not src or not os.path.exists(src):
            QMessageBox.warning(self, "Error", "Select valid PDF."); return
        if not out:
            QMessageBox.warning(self, "Error", "Choose output file."); return
        self.log.append(f"Rotating {src} by {self.angle_combo.currentText()}°")
        self.start_worker(pdf_ops.rotate_pdf, src, out,
                          int(self.angle_combo.currentText()), self.pages_edit.text().strip() or "all")


# ---------------- Delete / Extract ----------------

class _PagesTab(ToolTab):
    OPERATION = "delete_pages"
    BUTTON = "Apply"
    LABEL = "Pages:"

    def __init__(self):
        super().__init__()
        self.input_edit, _ = _file_row(self.main_layout, "Input PDF:", "PDF Files (*.pdf)")
        row = QHBoxLayout()
        row.addWidget(QLabel(self.LABEL))
        self.pages_edit = QLineEdit()
        self.pages_edit.setPlaceholderText("e.g. 1-3,5")
        row.addWidget(self.pages_edit)
        self.main_layout.addLayout(row)
        self.output_edit, _ = _file_row(
            self.main_layout, "Output PDF:", "PDF Files (*.pdf)", is_save=True)
        self.run_btn = QPushButton(self.BUTTON)
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def run(self):
        src = self.input_edit.text().strip()
        out = self.output_edit.text().strip()
        pages = self.pages_edit.text().strip()
        if not src or not os.path.exists(src):
            QMessageBox.warning(self, "Error", "Select valid PDF."); return
        if not out:
            QMessageBox.warning(self, "Error", "Choose output file."); return
        if not pages:
            QMessageBox.warning(self, "Error", "Enter page ranges."); return
        func = getattr(pdf_ops, self.OPERATION)
        self.log.append(f"{self.BUTTON}: pages {pages}")
        self.start_worker(func, src, out, pages)


class DeletePagesTab(_PagesTab):
    OPERATION = "delete_pages"
    BUTTON = "Delete Pages"
    LABEL = "Delete pages:"


class ExtractPagesTab(_PagesTab):
    OPERATION = "extract_pages"
    BUTTON = "Extract Pages"
    LABEL = "Extract pages:"


# ---------------- Protect / Unlock ----------------

class _PasswordTab(ToolTab):
    OPERATION = "protect_pdf"
    BUTTON = "Protect"
    PASSWORD_LABEL = "Password:"

    def __init__(self):
        super().__init__()
        self.input_edit, _ = _file_row(self.main_layout, "Input PDF:", "PDF Files (*.pdf)")
        row = QHBoxLayout()
        row.addWidget(QLabel(self.PASSWORD_LABEL))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        row.addWidget(self.pw_edit)
        self.main_layout.addLayout(row)
        self.output_edit, _ = _file_row(
            self.main_layout, "Output PDF:", "PDF Files (*.pdf)", is_save=True)
        self.run_btn = QPushButton(self.BUTTON)
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def run(self):
        src = self.input_edit.text().strip()
        out = self.output_edit.text().strip()
        pw = self.pw_edit.text()
        if not src or not os.path.exists(src):
            QMessageBox.warning(self, "Error", "Select valid PDF."); return
        if not out:
            QMessageBox.warning(self, "Error", "Choose output file."); return
        if not pw:
            QMessageBox.warning(self, "Error", "Enter password."); return
        func = getattr(pdf_ops, self.OPERATION)
        self.log.append(f"{self.BUTTON} {src}")
        self.start_worker(func, src, out, pw)


class ProtectTab(_PasswordTab):
    OPERATION = "protect_pdf"
    BUTTON = "Protect PDF"
    PASSWORD_LABEL = "Set password:"


class UnlockTab(_PasswordTab):
    OPERATION = "unlock_pdf"
    BUTTON = "Unlock PDF"
    PASSWORD_LABEL = "Current password:"


# ---------------- Image Size Reducer ----------------

class ImageReducerTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.main_layout.addWidget(QLabel(
            "Drag images here to reduce size (batch). Supports JPG, PNG, WEBP, BMP, TIFF."))
        self.list_widget = FileListWidget(
            lambda p: p.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")))
        self.main_layout.addWidget(self.list_widget)

        row = QHBoxLayout()
        for t, s in [("Add Images", self._add), ("Remove", self.list_widget.remove_selected),
                     ("Clear", self.list_widget.clear)]:
            b = QPushButton(t); b.clicked.connect(s); row.addWidget(b)
        self.main_layout.addLayout(row)

        qrow = QHBoxLayout()
        qrow.addWidget(QLabel("Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(75)
        self.quality_val = QLabel("75")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_val.setText(str(v)))
        qrow.addWidget(self.quality_slider)
        qrow.addWidget(self.quality_val)
        self.main_layout.addLayout(qrow)

        drow = QHBoxLayout()
        drow.addWidget(QLabel("Max dimension:"))
        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(0, 10000)
        self.max_dim_spin.setValue(0)
        self.max_dim_spin.setSuffix(" px  (0 = no resize)")
        drow.addWidget(self.max_dim_spin)
        drow.addStretch()
        self.main_layout.addLayout(drow)

        frow = QHBoxLayout()
        frow.addWidget(QLabel("Format:"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["Auto", "JPEG", "PNG", "WEBP"])
        frow.addWidget(self.fmt_combo)
        frow.addWidget(QLabel("Suffix:"))
        self.suffix_edit = QLineEdit("_reduced")
        frow.addWidget(self.suffix_edit)
        self.main_layout.addLayout(frow)

        orow = QHBoxLayout()
        orow.addWidget(QLabel("Output folder:"))
        self.out_edit = QLineEdit()
        orow.addWidget(self.out_edit)
        b = QPushButton("Browse"); b.clicked.connect(self._pick_out)
        orow.addWidget(b)
        self.main_layout.addLayout(orow)

        self.run_btn = QPushButton("Reduce Image Size")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _add(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add images", "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff)")
        self.list_widget.add_paths(paths)

    def _pick_out(self):
        p = QFileDialog.getExistingDirectory(self, "Output folder")
        if p:
            self.out_edit.setText(p)

    def run(self):
        paths = self.list_widget.paths()
        out = self.out_edit.text().strip()
        if not paths:
            QMessageBox.warning(self, "Error", "Add at least one image."); return
        if not out:
            QMessageBox.warning(self, "Error", "Select output folder."); return

        quality = self.quality_slider.value()
        max_dim = self.max_dim_spin.value()
        fmt = self.fmt_combo.currentText()
        suffix = self.suffix_edit.text() or "_reduced"

        self.log.append(f"Reducing {len(paths)} images (quality={quality}, "
                        f"max_dim={max_dim or 'none'}, format={fmt})")

        def task():
            results = pdf_ops.reduce_image_size(paths, out, quality, max_dim, fmt, suffix)
            total_before = sum(r[2] for r in results)
            total_after = sum(r[3] for r in results)
            saved = total_before - total_after
            pct = (saved / total_before * 100) if total_before else 0
            self.log.append(f"Before: {total_before/1024:.1f} KB")
            self.log.append(f"After:  {total_after/1024:.1f} KB")
            self.log.append(f"Saved:  {saved/1024:.1f} KB ({pct:.1f}%)")

        self.start_worker(task)


# ---------------- OCR ----------------

class OcrTab(ToolTab):
    def __init__(self):
        super().__init__()
        self.main_layout.addWidget(QLabel(
            "Extract text from images or scanned PDFs. Runs fully offline via Tesseract."))

        self.group = QButtonGroup(self)
        self.rb_images = QRadioButton("Images → Text (batch, one .txt per image)")
        self.rb_pdf = QRadioButton("PDF → Text (OCR the whole PDF)")
        self.rb_images.setChecked(True)
        self.group.addButton(self.rb_images)
        self.group.addButton(self.rb_pdf)
        self.main_layout.addWidget(self.rb_images)
        self.main_layout.addWidget(self.rb_pdf)

        self.images_box = QWidget()
        ib = QVBoxLayout(self.images_box)
        ib.setContentsMargins(0, 0, 0, 0)
        ib.addWidget(QLabel("Drag images here."))
        self.list_widget = FileListWidget(
            lambda p: p.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")))
        self.list_widget.setMinimumHeight(120)
        ib.addWidget(self.list_widget)
        row = QHBoxLayout()
        for t, s in [("Add Images", self._add), ("Remove", self.list_widget.remove_selected),
                     ("Clear", self.list_widget.clear)]:
            b = QPushButton(t); b.clicked.connect(s); row.addWidget(b)
        ib.addLayout(row)
        self.main_layout.addWidget(self.images_box)

        self.pdf_box = QWidget()
        pb = QVBoxLayout(self.pdf_box)
        pb.setContentsMargins(0, 0, 0, 0)
        prow = QHBoxLayout()
        prow.addWidget(QLabel("Input PDF:"))
        self.pdf_edit = QLineEdit()
        self.pdf_edit.setPlaceholderText("Select PDF...")
        prow.addWidget(self.pdf_edit)
        pbtn = QPushButton("Browse")
        pbtn.clicked.connect(self._pick_pdf)
        prow.addWidget(pbtn)
        pb.addLayout(prow)
        self.main_layout.addWidget(self.pdf_box)
        self.pdf_box.hide()
        self.rb_pdf.toggled.connect(self._switch_mode)

        opt = QHBoxLayout()
        opt.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["eng", "hin", "eng+hin", "fra", "deu", "spa", "ita", "por", "rus", "ara", "chi_sim"])
        opt.addWidget(self.lang_combo)
        opt.addWidget(QLabel("DPI (PDF):"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(150, 600)
        self.dpi_spin.setValue(300)
        opt.addWidget(self.dpi_spin)
        opt.addStretch()
        self.main_layout.addLayout(opt)

        psm_row = QHBoxLayout()
        psm_row.addWidget(QLabel("Layout mode:"))
        self.psm_combo = QComboBox()
        self.psm_combo.addItems([
            "3 — Auto (mixed page)",
            "4 — Single column of text",
            "6 — Single uniform block",
            "11 — Sparse text (find as much as possible)",
            "12 — Sparse text + orientation detection",
            "1 — Auto with OSD (rotated pages)",
        ])
        psm_row.addWidget(self.psm_combo, 1)
        self.main_layout.addLayout(psm_row)

        hint = QLabel("💡 If text is incomplete, try <b>11 (Sparse text)</b>.")
        hint.setStyleSheet("color:#666; font-size: 11px;")
        self.main_layout.addWidget(hint)

        orow = QHBoxLayout()
        orow.addWidget(QLabel("Output folder:"))
        self.out_edit = QLineEdit()
        orow.addWidget(self.out_edit)
        ob = QPushButton("Browse"); ob.clicked.connect(self._pick_out)
        orow.addWidget(ob)
        self.main_layout.addLayout(orow)

        self.run_btn = QPushButton("Extract Text from Images")
        self.run_btn.clicked.connect(self.run)
        self.main_layout.addWidget(self.run_btn)
        self.add_progress_and_log()

    def _switch_mode(self):
        pdf = self.rb_pdf.isChecked()
        self.images_box.setVisible(not pdf)
        self.pdf_box.setVisible(pdf)
        self.run_btn.setText("Extract Text from PDF" if pdf
                             else "Extract Text from Images")

    def _add(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add images", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp)")
        self.list_widget.add_paths(paths)

    def _pick_pdf(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if p:
            self.pdf_edit.setText(p)

    def _pick_out(self):
        p = QFileDialog.getExistingDirectory(self, "Output folder")
        if p:
            self.out_edit.setText(p)

    def _current_psm(self):
        return int(self.psm_combo.currentText().split("—")[0].strip())

    def run(self):
        out = self.out_edit.text().strip()
        lang = self.lang_combo.currentText()
        psm = self._current_psm()
        if not out:
            QMessageBox.warning(self, "Error", "Choose an output folder."); return

        if self.rb_pdf.isChecked():
            src = self.pdf_edit.text().strip()
            if not src or not os.path.exists(src):
                QMessageBox.warning(self, "Error", "Select a valid PDF."); return
            base = os.path.splitext(os.path.basename(src))[0]
            out_txt = os.path.join(out, f"{base}_ocr.txt")
            dpi = self.dpi_spin.value()
            self.log.append(f"OCR PDF ({lang}, {dpi} DPI, PSM {psm}) → {out_txt}")
            self.start_worker(pdf_ops.ocr_pdf_to_text, src, out_txt, dpi, lang, psm)
        else:
            paths = self.list_widget.paths()
            if not paths:
                QMessageBox.warning(self, "Error", "Add at least one image."); return
            self.log.append(f"OCR {len(paths)} images ({lang}, PSM {psm}) → {out}")
            self.start_worker(pdf_ops.ocr_images_to_text, paths, out, lang, psm)


# ---------------- About tab ----------------

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        from PySide6.QtWidgets import QTextBrowser
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; color: #222;">
          <h1 style="margin-bottom:0;">{APP_NAME}</h1>
          <p style="color:#666; margin-top:4px;">Version {APP_VERSION} &nbsp;·&nbsp; Offline PDF &amp; Image Toolkit</p>

          <h3>👤 About the Author</h3>
          <p>
            Created by <b>{APP_AUTHOR}</b>.<br>
            A free, offline desktop toolkit for PDFs and images — no uploads, no accounts,
            no internet required.
          </p>
          <p>
            🌐 <a href="{APP_WEBSITE}">Website</a> &nbsp;·&nbsp;
            💻 <a href="{APP_GITHUB}">GitHub</a> &nbsp;·&nbsp;
            🔗 <a href="{APP_LINKEDIN}">LinkedIn</a>
          </p>

          <h3>✨ Features</h3>
          <ul>
            <li><b>Compress PDF</b> — manual quality/DPI control or auto target size</li>
            <li><b>Merge PDF</b> — combine multiple files in your chosen order</li>
            <li><b>Split PDF</b> — every page or by custom ranges (1-3,4-6)</li>
            <li><b>Images → PDF</b> — batch convert with A4/Letter/Legal/Fit sizes</li>
            <li><b>PDF → Images</b> — export pages as PNG or JPG at custom DPI</li>
            <li><b>Rotate</b> — 90° / 180° / 270°, on any page range</li>
            <li><b>Delete Pages</b> / <b>Extract Pages</b></li>
            <li><b>Protect PDF</b> — set a password</li>
            <li><b>Unlock PDF</b> — remove a known password</li>
            <li><b>Image Size Reducer</b> — batch resize + recompress</li>
            <li><b>OCR / Text Extractor</b> — extract text from images or scanned PDFs</li>
          </ul>

          <h3>🔒 Privacy</h3>
          <p>Everything runs locally on your PC. No file ever leaves your computer.</p>

          <h3>📄 License</h3>
          <p>Powered by Ghostscript and Tesseract under the hood.<br>
          © {__import__('datetime').datetime.now().year} {APP_AUTHOR}. All rights reserved.</p>
        </div>
        """)
        layout.addWidget(browser)


# ---------------- Main window ----------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(960, 720)

        tabs = QTabWidget()
        tabs.addTab(CompressTab(), "Compress PDF")
        tabs.addTab(MergeTab(), "Merge PDF")
        tabs.addTab(SplitTab(), "Split PDF")
        tabs.addTab(ImagesToPdfTab(), "Images → PDF")
        tabs.addTab(PdfToImagesTab(), "PDF → Images")
        tabs.addTab(RotateTab(), "Rotate")
        tabs.addTab(DeletePagesTab(), "Delete Pages")
        tabs.addTab(ExtractPagesTab(), "Extract Pages")
        tabs.addTab(ProtectTab(), "Protect")
        tabs.addTab(UnlockTab(), "Unlock")
        tabs.addTab(ImageReducerTab(), "Image Size Reducer")
        tabs.addTab(OcrTab(), "OCR / Text Extractor")
        tabs.addTab(AboutTab(), "About")
        self.setCentralWidget(tabs)

        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(f"About {APP_NAME}", self._show_about)

    def _show_about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME}</h3>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>Created by <b>{APP_AUTHOR}</b></p>"
            f"<p>"
            f"<a href='{APP_WEBSITE}'>Website</a> &nbsp;|&nbsp; "
            f"<a href='{APP_GITHUB}'>GitHub</a> &nbsp;|&nbsp; "
            f"<a href='{APP_LINKEDIN}'>LinkedIn</a>"
            f"</p>"
            f"<p>© {__import__('datetime').datetime.now().year} {APP_AUTHOR}.</p>"
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_AUTHOR)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()