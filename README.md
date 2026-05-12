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

Screenshots Program
1. Tampilan Awal
<img width="1282" height="772" alt="image" src="https://github.com/user-attachments/assets/178d0a85-dbc2-4633-996f-691b7ec26c39" />
2. Form Tambah Post
<img width="1282" height="772" alt="image" src="https://github.com/user-attachments/assets/fcbdc622-268a-4f01-95e4-2871da10407a" />
3. Form Edit Post
<img width="1282" height="772" alt="image" src="https://github.com/user-attachments/assets/276291a0-a1eb-46dd-a876-8fef472e257a" />
4. Hapus Post
<img width="1282" height="772" alt="image" src="https://github.com/user-attachments/assets/97aea383-57be-4335-b990-b4e4f810b577" />
