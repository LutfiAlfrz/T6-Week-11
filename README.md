### Post Manager
Aplikasi desktop untuk mengelola data post melalui REST API, dibangun menggunakan Python, PySide6, dan Threading sebagai tugas mata kuliah Pemrograman Visual.

Fitur Aplikasi
1. Tampilkan Daftar Post — memuat semua post dari server dan menampilkannya dalam tabel
2. Detail Post — klik baris tabel untuk melihat isi lengkap post beserta komentar di panel samping
3. Tambah Post — form input untuk membuat post baru via POST request
4. Edit Post — ubah data post yang dipilih via PUT request
5. Hapus Post — hapus post beserta semua komentarnya via DELETE request, dilengkapi dialog konfirmasi
6. Pencarian — filter post berdasarkan judul atau author secara lokal
7. Non-blocking UI — semua request API berjalan di thread terpisah sehingga UI tidak pernah freeze
