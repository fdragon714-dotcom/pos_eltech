# Agent Workflow — POS El-Tech

## Tujuan
Panduan kerja wajib yang harus diikuti setiap kali mengimplementasikan fitur baru atau perubahan di project POS El-Tech.

---

## Struktur Direktori

```
c:\Users\claud\pos_eltech2\          ← Root Git Repository
│   .git\
│   pos_eltech\                      ← Root Project Django
│   │   docs\
│   │   │   prd.md                   ← Sumber kebenaran: apa yang harus dibangun
│   │   │   task.md                  ← Daftar tugas: apa yang sudah & belum dikerjakan
│   │   │   agent.md                 ← File ini
│   │   posApp\
│   │   │   models.py
│   │   │   views.py
│   │   │   urls.py
│   │   │   admin.py
│   │   │   templates\posApp\
│   │   pos\
│   │   │   settings.py
│   │   manage.py
│   │   db.sqlite3
│   venv\
```

---

## Alur Kerja Wajib (Harus Diikuti Setiap Sesi)

### LANGKAH 0 — Baca Konteks (SELALU LAKUKAN PERTAMA)

Sebelum menulis satu baris kode pun:

1. Baca `docs/prd.md` → pahami apa yang harus dibangun, spesifikasi halaman, dan struktur tabel
2. Baca `docs/task.md` → pahami apa yang sudah selesai (`[x]`) dan apa yang belum (`[ ]`)
3. Tentukan task berikutnya berdasarkan **urutan pengerjaan** yang ada di task.md
4. Konfirmasi ke user task mana yang akan dikerjakan sebelum mulai

---

### LANGKAH 1 — Implementasi

Kerjakan satu kelompok task (A, B, C, dst.) secara tuntas:

- Ikuti spesifikasi di `prd.md` dengan tepat (nama field, tipe data, logika, URL)
- Jangan skip atau modifikasi spesifikasi tanpa konfirmasi user
- Jika ada ambiguitas → tanyakan dulu, jangan asumsi

---

### LANGKAH 2 — Verifikasi Setelah Setiap Perubahan

Setelah setiap kelompok task selesai, jalankan pemeriksaan berikut:

#### Untuk perubahan Model/Migrasi:
```powershell
cd c:\Users\claud\pos_eltech2\pos_eltech
python manage.py check
python manage.py showmigrations posApp
```

#### Untuk perubahan Views/URL:
```powershell
cd c:\Users\claud\pos_eltech2\pos_eltech
python manage.py check
# Pastikan tidak ada ImportError atau URL conflict
```

#### Untuk semua perubahan:
```powershell
cd c:\Users\claud\pos_eltech2\pos_eltech
python manage.py check --deploy 2>&1 | Select-String -Pattern "Error|Warning" | head -20
```

Jika ada error → perbaiki dulu sebelum lanjut ke langkah 3.

---

### LANGKAH 3 — Update task.md

Setelah verifikasi berhasil, tandai task yang selesai:

- Ubah `- [ ]` menjadi `- [x]` untuk setiap item yang selesai
- Simpan file `docs/task.md`

Format centang:
```markdown
- [x] Buat model InventoryLog  ← selesai
- [ ] Jalankan migrasi         ← belum
```

---

### LANGKAH 4 — Git Commit & Push

Setelah task.md diupdate, langsung commit dan push:

```powershell
cd c:\Users\claud\pos_eltech2

# Stage semua perubahan
git add .

# Commit dengan pesan yang deskriptif
git commit -m "[TASK X] Deskripsi singkat apa yang dilakukan"

# Push ke remote
git push origin main
```

#### Format Pesan Commit:

| Kelompok Task | Prefix Commit |
|---|---|
| A — Model | `[TASK A] Add InventoryLog model & migration` |
| B — Integrasi POS | `[TASK B] Add inventory auto-log to save_pos & delete_sale` |
| C — Views | `[TASK C] Add inventory views (list, add, adjust, product, low-stock)` |
| D — URL | `[TASK D] Register inventory URLs` |
| E — Templates | `[TASK E] Add inventory HTML templates` |
| F — Navigasi | `[TASK F] Add inventory menu to sidebar navigation` |
| G — Admin | `[TASK G] Register InventoryLog to Django Admin` |
| H — Import | `[TASK H] Update model imports in views.py` |
| Fix/Hotfix | `[FIX] Deskripsi bug yang diperbaiki` |

---

### LANGKAH 5 — Laporan ke User

Setelah push berhasil, beri laporan singkat:

```
✅ Task [X] selesai — [deskripsi]
📋 task.md diupdate
🔀 Git commit: "[pesan commit]"
🚀 Pushed ke origin/main

Task berikutnya: [Y] — [deskripsi task Y]
```

---

## Aturan Tambahan

### Jangan lakukan ini:
- ❌ Commit jika `python manage.py check` masih ada error
- ❌ Skip update task.md sebelum commit
- ❌ Ubah spesifikasi tabel/field tanpa konfirmasi user
- ❌ Menggabungkan beberapa kelompok task dalam satu commit (kecuali sangat trivial)

### Selalu lakukan ini:
- ✅ Cek PRD dan task.md di awal setiap sesi kerja baru
- ✅ Satu commit per kelompok task
- ✅ Verifikasi `manage.py check` sebelum commit
- ✅ Update task.md sebelum git add

---

## Git Remote Info

```
Remote: origin
URL:    https://github.com/fdragon714-dotcom/pos_eltech.git
Branch: main
Root:   c:\Users\claud\pos_eltech2\
```

## Django Server

Server development berjalan di:
```powershell
cd c:\Users\claud\pos_eltech2\pos_eltech
.\venv\Scripts\activate   # atau: ..\venv\Scripts\activate dari folder pos_eltech
python manage.py runserver
```
Akses: http://127.0.0.1:8000

---

## Referensi Cepat

| File | Fungsi |
|---|---|
| `docs/prd.md` | Spesifikasi lengkap semua modul, halaman, dan tabel |
| `docs/task.md` | Daftar task dan status penyelesaian |
| `posApp/models.py` | Semua model database |
| `posApp/views.py` | Semua logic halaman |
| `posApp/urls.py` | Routing URL |
| `posApp/admin.py` | Konfigurasi Django Admin (Unfold) |
| `posApp/templates/posApp/` | Semua file HTML template |
| `posApp/templates/posApp/navigation.html` | Sidebar navigasi |
| `pos/settings.py` | Konfigurasi Django + Unfold sidebar |
