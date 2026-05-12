# Nama  : Lutfi Alfarizi
# NIM   : F1D02310121
# Kelas : C

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QGroupBox, QLabel, QVBoxLayout,
    QHBoxLayout, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt

class DeleteDialog(QDialog):

    def __init__(self, post_title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfirmasi Hapus")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)

        icon = QLabel("🗑️")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size:36px; margin:8px;")
        layout.addWidget(icon)

        msg = QLabel(
            f'Yakin ingin menghapus post:\n\n"{post_title}"?\n\n'
            "Semua komentar pada post ini juga akan ikut terhapus."
        )
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg)

        btns = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Yes).setText("Ya, Hapus")
        btns.button(QDialogButtonBox.Yes).setStyleSheet(
            "background:#e74c3c; color:white; font-weight:bold;"
            " padding:6px 16px; border-radius:4px;"
        )
        btns.button(QDialogButtonBox.Cancel).setText("Batal")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

class DetailPanel(QGroupBox):
    def __init__(self):
        super().__init__("Detail Post")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        def field_label(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight:bold; color:#555; font-size:11px;")
            return lbl

        # Judul
        layout.addWidget(field_label("JUDUL"))
        self.title_val = QLabel("—")
        self.title_val.setWordWrap(True)
        self.title_val.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#2c3e50; margin-bottom:6px;"
        )
        layout.addWidget(self.title_val)

        # Author
        layout.addWidget(field_label("AUTHOR"))
        self.author_val = QLabel("—")
        self.author_val.setStyleSheet("color:#7f8c8d; margin-bottom:6px;")
        layout.addWidget(self.author_val)

        # Slug
        layout.addWidget(field_label("SLUG"))
        self.slug_val = QLabel("—")
        self.slug_val.setStyleSheet(
            "color:#7f8c8d; font-family:monospace; margin-bottom:6px;"
        )
        layout.addWidget(self.slug_val)

        # Status
        layout.addWidget(field_label("STATUS"))
        self.status_val = QLabel("—")
        self.status_val.setStyleSheet("margin-bottom:6px;")
        layout.addWidget(self.status_val)

        # Body
        layout.addWidget(field_label("ISI KONTEN"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.body_val = QLabel("—")
        self.body_val.setWordWrap(True)
        self.body_val.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.body_val.setStyleSheet(
            "padding:6px; background:#f9f9f9; border-radius:4px;"
        )
        scroll.setWidget(self.body_val)
        scroll.setMinimumHeight(120)
        layout.addWidget(scroll)

        # Komentar
        layout.addWidget(field_label("KOMENTAR"))
        self.comments_val = QLabel("Klik baris tabel untuk melihat detail & komentar.")
        self.comments_val.setWordWrap(True)
        self.comments_val.setStyleSheet("color:#7f8c8d; font-size:12px;")
        layout.addWidget(self.comments_val)

        layout.addStretch()

    def show_post(self, post: dict, comments=None) -> None:
        self.title_val.setText(post.get("title", "—"))
        self.author_val.setText(post.get("author", "—"))
        self.slug_val.setText(post.get("slug", "—"))
        self.body_val.setText(post.get("body", "—"))

        status = str(post.get("status", "—"))
        color  = "#27ae60" if status.lower() == "published" else "#e67e22"
        self.status_val.setText(status.capitalize())
        self.status_val.setStyleSheet(
            f"color:white; background:{color}; padding:2px 10px;"
            f" border-radius:10px; font-weight:bold; font-size:11px; margin-bottom:6px;"
        )

        if comments is None:
            self.comments_val.setText("Memuat komentar…")
        elif comments:
            lines = [
                f"💬 {c.get('author', '?')}: {c.get('body', '')}"
                for c in comments
            ]
            self.comments_val.setText("\n\n".join(lines))
        else:
            self.comments_val.setText("Tidak ada komentar.")

    def clear(self) -> None:
        for widget in (
            self.title_val, self.author_val, self.slug_val,
            self.body_val, self.comments_val,
        ):
            widget.setText("—")
        self.status_val.setText("—")
        self.status_val.setStyleSheet("color:#7f8c8d; margin-bottom:6px;")

class PostForm(QGroupBox):
    def __init__(self):
        super().__init__("Form Post")
        layout = QVBoxLayout(self)

        def add_row(label_text: str, widget) -> None:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight:bold; font-size:11px; color:#555;")
            layout.addWidget(lbl)
            layout.addWidget(widget)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul post…")
        self.title_input.setStyleSheet("color:#2c3e50; background:white; padding:4px;")

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Nama penulis…")
        self.author_input.setStyleSheet("color:#2c3e50; background:white; padding:4px;")

        self.slug_input = QLineEdit()
        self.slug_input.setPlaceholderText("contoh-slug-unik")
        self.slug_input.setStyleSheet("color:#2c3e50; background:white; padding:4px;")

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Isi konten post…")
        self.body_input.setMinimumHeight(90)
        self.body_input.setStyleSheet("color:#2c3e50; background:white; padding:4px;")

        self.status_input = QComboBox()
        self.status_input.addItems(["published", "draft"])
        self.status_input.setStyleSheet("color:#2c3e50; background:white; padding:4px;")

        add_row("JUDUL *",   self.title_input)
        add_row("AUTHOR *",  self.author_input)
        add_row("SLUG *",    self.slug_input)
        add_row("KONTEN *",  self.body_input)
        add_row("STATUS",    self.status_input)

        btn_row = QHBoxLayout()
        self.btn_save   = QPushButton("💾 Simpan")
        self.btn_cancel = QPushButton("✖ Batal")
        self.btn_save.setStyleSheet(
            "background:#2980b9; color:white; font-weight:bold;"
            " padding:7px 20px; border-radius:4px;"
        )
        self.btn_cancel.setStyleSheet(
            "background:#bdc3c7; color:#333; padding:7px 20px; border-radius:4px;"
        )
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

    def fill(self, post: dict) -> None:
        self.title_input.setText(post.get("title", ""))
        self.author_input.setText(post.get("author", ""))
        self.slug_input.setText(post.get("slug", ""))
        self.body_input.setPlainText(post.get("body", ""))
        idx = self.status_input.findText(post.get("status", "published"))
        self.status_input.setCurrentIndex(idx if idx >= 0 else 0)

    def get_data(self) -> dict:
        return {
            "title":  self.title_input.text().strip(),
            "author": self.author_input.text().strip(),
            "slug":   self.slug_input.text().strip(),
            "body":   self.body_input.toPlainText().strip(),
            "status": self.status_input.currentText(),
        }

    def clear(self) -> None:
        for widget in (self.title_input, self.author_input, self.slug_input):
            widget.clear()
        self.body_input.clear()
        self.status_input.setCurrentIndex(0)

    def validate(self) -> str | None:
        data = self.get_data()
        for label, value in [
            ("Judul",  data["title"]),
            ("Author", data["author"]),
            ("Slug",   data["slug"]),
            ("Konten", data["body"]),
        ]:
            if not value:
                return f"Field '{label}' tidak boleh kosong."
        return None