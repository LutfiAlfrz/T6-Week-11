import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QLineEdit,
    QSplitter, QMessageBox, QHeaderView, QDialog,
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QColor, QFont, QPalette

from api_service import PostApiService
from api_worker  import ApiWorker, run_worker
from dialogs     import DeleteDialog, DetailPanel, PostForm

from config import BASE_URL, TIMEOUT
print(f"[DEBUG] BASE_URL = '{BASE_URL}'")
print(f"[DEBUG] URL yang akan dipanggil = '{BASE_URL}/posts'")

class PostManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager")
        self.resize(1280, 740)

        self._service       = PostApiService()
        self._posts: list   = []
        self._selected_post = None
        self._edit_mode     = False
        self._threads: list = []

        self._build_ui()
        self._action_load_all()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(8)

        # Header
        header = QLabel("📋 Post Manager")
        header.setStyleSheet("font-size:20px; font-weight:bold; color:#2c3e50;")
        root.addWidget(header)

        # Toolbar
        root.addLayout(self._build_toolbar())

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self._build_table(), 2)

        self.form = PostForm()
        self.form.setVisible(False)
        self.form.btn_save.clicked.connect(self._action_save)
        self.form.btn_cancel.clicked.connect(self._cancel_form)
        left_layout.addWidget(self.form, 1)

        splitter.addWidget(left)

        self.detail = DetailPanel()
        splitter.addWidget(self.detail)
        splitter.setSizes([780, 380])

        self.statusBar().showMessage("Siap.")

    def _build_toolbar(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_add     = QPushButton("➕ Tambah Post")
        self.btn_edit    = QPushButton("✏️ Edit")
        self.btn_delete  = QPushButton("🗑️ Hapus")

        colors = {
            self.btn_refresh: "#27ae60",
            self.btn_add:     "#2980b9",
            self.btn_edit:    "#e67e22",
            self.btn_delete:  "#e74c3c",
        }
        for btn, color in colors.items():
            btn.setStyleSheet(
                f"background:{color}; color:white; font-weight:bold;"
                f" padding:7px 16px; border-radius:4px; font-size:13px;"
            )
            layout.addWidget(btn)

        # Edit & Hapus nonaktif sampai ada baris dipilih
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        self.btn_refresh.clicked.connect(self._action_load_all)
        self.btn_add.clicked.connect(self._show_add_form)
        self.btn_edit.clicked.connect(self._show_edit_form)
        self.btn_delete.clicked.connect(self._action_delete)

        layout.addStretch()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Cari judul atau author…")
        self.search_box.setMinimumWidth(220)
        self.search_box.setStyleSheet(
            "padding:6px; border:1px solid #bdc3c7; border-radius:4px;"
        )
        self.search_box.textChanged.connect(self._filter_table)
        layout.addWidget(self.search_box)

        return layout

    def _build_table(self) -> QTableWidget:
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Author", "Status"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.table.setStyleSheet("""
            QTableWidget { border:1px solid #dde; font-size:13px; }
            QHeaderView::section {
                background:#2c3e50; color:white;
                padding:6px; font-weight:bold; border:none;
            }
            QTableWidget::item:selected { background:#2980b9; color:white; }
            QTableWidget::item { padding:4px; color:#2c3e50; }
        """)

        self.table.selectionModel().selectionChanged.connect(self._on_row_selected)
        self.table.doubleClicked.connect(self._action_load_detail)
        return self.table

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self.btn_refresh.setEnabled(not busy)
        self.btn_add.setEnabled(not busy)
        has_sel = self._selected_post is not None
        self.btn_edit.setEnabled(not busy and has_sel)
        self.btn_delete.setEnabled(not busy and has_sel)
        self.statusBar().showMessage(message if busy else "Siap.")

    def _keep_thread(self, thread: QThread) -> None:
        self._threads.append(thread)
        thread.finished.connect(
            lambda: self._threads.remove(thread) if thread in self._threads else None
        )
    
    def _keep_worker(self, worker: ApiWorker, thread: QThread) -> None:
        self._threads.append((worker, thread))
        thread.finished.connect(
            lambda: self._threads.remove((worker, thread))
            if (worker, thread) in self._threads else None
        )

    def _show_error(self, message: str) -> None:
        self._set_busy(False)
        QMessageBox.critical(self, "Error", message)

    def _show_success(self, message: str) -> None:
        self.statusBar().showMessage(f"✅ {message}", 4000)

    def _filter_table(self, text: str) -> None:
        keyword = text.lower()
        for row in range(self.table.rowCount()):
            title  = self.table.item(row, 1).text().lower() if self.table.item(row, 1) else ""
            author = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""
            self.table.setRowHidden(row, keyword not in title and keyword not in author)

    def _populate_table(self, posts: list) -> None:
        self.table.setRowCount(0)
        for post in posts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(post.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(post.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(post.get("author", "")))

            status = str(post.get("status", ""))
            s_item = QTableWidgetItem(status.capitalize())
            s_item.setForeground(
                QColor("#27ae60") if status.lower() == "published" else QColor("#e67e22")
            )
            s_item.setFont(QFont("", -1, QFont.Bold))
            self.table.setItem(row, 3, s_item)

    def _on_row_selected(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self._selected_post = None
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return

        row = rows[0].row()
        if self.table.isRowHidden(row):
            return

        post_id = int(self.table.item(row, 0).text())
        self._selected_post = next(
            (p for p in self._posts if p["id"] == post_id), None
        )
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self._action_load_detail()

    def _action_load_all(self) -> None:
        self._set_busy(True, "⏳ Memuat daftar post…")
        worker = ApiWorker(self._service.get_all_posts)
        worker.finished.connect(self._on_all_loaded)
        worker.error.connect(self._show_error)
        thread = run_worker(worker)
        self._keep_worker(worker, thread)

    def _on_all_loaded(self, data: dict) -> None:
        print(f"[DEBUG] _on_all_loaded dipanggil, data keys: {data.keys()}")
        print(f"[DEBUG] Jumlah post: {len(data.get('data', []))}")
        self._posts = data.get("data", [])
        self._populate_table(self._posts)
        self._set_busy(False)
        self._show_success(f"{len(self._posts)} post dimuat.")
        self._selected_post = None
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.detail.clear()

    def _action_load_detail(self) -> None:
        if not self._selected_post:
            return
        post_id = self._selected_post["id"]
        # Tampilkan data lokal dulu; komentar menyusul
        self.detail.show_post(self._selected_post, None)
        self._set_busy(True, f"⏳ Memuat detail post #{post_id}…")

        worker = ApiWorker(self._service.get_post, post_id)
        worker.finished.connect(self._on_detail_loaded)
        worker.error.connect(
            lambda e: (self._show_error(e),
                       self.detail.show_post(self._selected_post, []))
        )
        thread = run_worker(worker)
        self._keep_worker(worker, thread)

    def _on_detail_loaded(self, data: dict) -> None:
        self._set_busy(False)
        post     = data.get("data", {})
        comments = post.get("comments", [])
        self.detail.show_post(post, comments)

    def _show_add_form(self) -> None:
        self._edit_mode = False
        self.form.clear()
        self.form.setTitle("➕ Tambah Post Baru")
        self.form.setVisible(True)

    def _show_edit_form(self) -> None:
        if not self._selected_post:
            return
        self._edit_mode = True
        self.form.fill(self._selected_post)
        self.form.setTitle(f"✏️ Edit Post #{self._selected_post['id']}")
        self.form.setVisible(True)

    def _cancel_form(self) -> None:
        self.form.setVisible(False)
        self.form.clear()
        self._edit_mode = False

    def _action_save(self) -> None:
        # Validasi sisi klien
        error = self.form.validate()
        if error:
            QMessageBox.warning(self, "Validasi", error)
            return

        payload = self.form.get_data()

        if self._edit_mode and self._selected_post:
            post_id = self._selected_post["id"]
            worker  = ApiWorker(self._service.update_post, post_id, payload)
            msg     = f"⏳ Menyimpan perubahan post #{post_id}…"
        else:
            worker = ApiWorker(self._service.create_post, payload)
            msg    = "⏳ Menambahkan post baru…"

        self._set_busy(True, msg)
        worker.finished.connect(self._on_save_done)
        worker.error.connect(self._show_error)
        thread = run_worker(worker)
        self._keep_worker(worker, thread)

    def _on_save_done(self, data: dict) -> None:
        self._set_busy(False)
        self.form.setVisible(False)
        self.form.clear()

        if self._edit_mode:
            self._show_success("Post berhasil diperbarui!")
        else:
            new_id = data.get("data", {}).get("id", "?")
            self._show_success(f"Post baru ditambahkan! ID: {new_id}")

        self._edit_mode = False
        self._action_load_all()

    def _action_delete(self) -> None:
        if not self._selected_post:
            return

        dlg = DeleteDialog(self._selected_post.get("title", ""), self)
        if dlg.exec() != QDialog.Accepted:
            return

        post_id = self._selected_post["id"]
        self._set_busy(True, f"⏳ Menghapus post #{post_id}…")

        worker = ApiWorker(self._service.delete_post, post_id)
        worker.finished.connect(self._on_delete_done)
        worker.error.connect(self._show_error)
        thread = run_worker(worker)
        self._keep_worker(worker, thread)

    def _on_delete_done(self, _) -> None:
        self._set_busy(False)
        self._show_success("Post berhasil dihapus!")
        self._selected_post = None
        self.detail.clear()
        self._action_load_all()

def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = app.palette()
    pal.setColor(QPalette.Window,        QColor("#f0f2f5"))
    pal.setColor(QPalette.WindowText,    QColor("#2c3e50"))
    pal.setColor(QPalette.Base,          QColor("#ffffff"))
    pal.setColor(QPalette.AlternateBase, QColor("#f7f9fc"))
    pal.setColor(QPalette.Button,        QColor("#ecf0f1"))
    pal.setColor(QPalette.ButtonText,    QColor("#2c3e50"))
    app.setPalette(pal)

    window = PostManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()