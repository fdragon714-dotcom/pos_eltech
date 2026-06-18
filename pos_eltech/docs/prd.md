# PRD — Sistem POS El-Tech
**Versi:** 2.0 | **Update:** 19 Juni 2026

---

## Overview

Sistem POS berbasis web untuk UMKM El-Tech — toko laptop bekas di Pontianak. Dijalankan di **localhost** menggunakan **Django + SQLite**. Dua role pengguna: **Admin** (pemilik) dan **Kasir**.

---

## User Roles & Akses

| Fitur | Admin | Kasir |
|---|:---:|:---:|
| Login / Logout | ✅ | ✅ |
| Lihat Dashboard | ✅ | ✅ |
| Lihat Produk & Kategori | ✅ | ✅ |
| Tambah / Edit / Hapus Produk | ✅ | ❌ |
| Tambah / Edit / Hapus Kategori | ✅ | ❌ |
| Proses Transaksi POS | ✅ | ✅ |
| Lihat Riwayat Penjualan | ✅ | ✅ |
| Hapus Transaksi | ✅ | ❌ |
| Lihat Log Inventory | ✅ | ✅ |
| Catat Stok Masuk (Manual) | ✅ | ❌ |
| Penyesuaian Stok | ✅ | ❌ |
| Kelola Akun Pengguna (`/admin`) | ✅ | ❌ |

---

## Modul & Halaman

---

### 1. Autentikasi

#### `GET /login` — Halaman Login
- Form: username + password
- Jika sukses → redirect ke `/`
- Jika sudah login → langsung redirect ke `/`
- Membedakan Admin (`is_superuser=True`) dan Kasir secara otomatis via Django auth

---

### 2. Dashboard

#### `GET /` — Beranda
**4 Kartu Statistik** (difilter berdasarkan periode):
- Total Kategori, Total Produk, Jumlah Transaksi, Total Pendapatan

**Filter Periode:** Hari Ini / Minggu Ini / Bulan Ini / Tahun Ini

**Grafik Pendapatan** (area chart):
- Hari Ini → per jam
- Minggu Ini → per hari (Sen–Min)
- Bulan Ini → per tanggal
- Tahun Ini → per bulan

**Indikator Growth:** persentase naik/turun vs periode sebelumnya

**Tabel Top 5 Produk Terlaris** (bisa difilter periode): Kode, Nama, Merek, Total Qty Terjual

---

### 3. Kategori & Merek

#### `GET /category` — Daftar Kategori
Tabel: Foto · Nama · Deskripsi · Status · Tanggal Dibuat
Aksi: Tambah (Admin), Edit (Admin), Hapus (Admin)

#### `GET/POST /manage_category` — Form Tambah/Edit Kategori
Field: Nama, Deskripsi, Upload Foto, Status (Aktif/Nonaktif)
Sub-seksi Tipe Merek: bisa tambah/hapus tipe (mis. Asus Gaming, Asus Bisnis)

**Tabel: `posApp_category`**
| Kolom | Tipe | Catatan |
|---|---|---|
| `id` | BigAutoField PK | |
| `name` | CharField(50) | Nama merek |
| `description` | TextField | |
| `image` | ImageField | `media/category_images/` |
| `status` | IntegerField | 1=Aktif, 0=Nonaktif |
| `date_added` | DateTimeField | default=now |
| `date_updated` | DateTimeField | auto_now |

**Tabel: `posApp_categorytype`**
| Kolom | Tipe | Catatan |
|---|---|---|
| `id` | BigAutoField PK | |
| `category` | FK → category | CASCADE |
| `name` | CharField(30) | Nama tipe |
| `image` | ImageField | `media/type_images/` |

---

### 4. Produk

#### `GET /products` — Daftar Produk
Tabel: Foto · Kode SKU · Nama · Merek · Harga · Stok · Garansi · Status
Badge Stok: 🟢 >10 · 🟡 1–10 · 🔴 0
Aksi: Tambah (Admin), Edit (Admin), Hapus (Admin)

#### `GET/POST /manage_products` — Form Tambah/Edit Produk
Field: Kode SKU (unik), Nama, Merek (dropdown aktif), Deskripsi, Harga Jual, Stok, Garansi (hari), Upload Foto, Status

**Tabel: `posApp_products`**
| Kolom | Tipe | Catatan |
|---|---|---|
| `id` | BigAutoField PK | |
| `code` | CharField(10) | SKU, harus unik |
| `category_id` | FK → category | CASCADE |
| `name` | CharField(30) | |
| `description` | TextField | Spesifikasi produk |
| `price` | FloatField | Harga jual |
| `stock` | IntegerField | Stok saat ini |
| `warranty` | IntegerField | Garansi dalam hari, 0=non-garansi |
| `image` | ImageField | `media/product_images/` |
| `status` | IntegerField | 1=Aktif, 0=Arsip |
| `date_added` | DateTimeField | default=now |
| `date_updated` | DateTimeField | auto_now |

---

### 5. Point of Sale (Kasir)

#### `GET /pos` — Halaman Kasir
- **Kiri:** Grid kartu produk aktif (Foto, Nama, Harga, Stok)
- **Kanan:** Keranjang belanja — tabel (Nama, Harga, Qty, Subtotal, ❌ Hapus)
- **Bawah kanan:** Subtotal · Diskon (%) · Total Akhir · Tombol Checkout

#### Modal Checkout
- Total akhir
- Data Pelanggan (opsional): Nama, No. WA, Alamat
- Metode Bayar:
  - **Tunai** → input jumlah bayar → tampilkan kembalian
  - **QRIS** → tampilkan QR Code
  - **Transfer** → konfirmasi manual
- Tombol "Simpan Transaksi"

**Yang terjadi saat transaksi disimpan:**
1. Data tersimpan ke `posApp_sales` + `posApp_salesitems`
2. Stok tiap produk terjual otomatis dikurangi (`stock -= qty`)
3. **[INVENTORY]** Log `KELUAR` otomatis dicatat ke `posApp_inventorylog` per item

**Validasi:** Stok tidak boleh < 0 saat checkout

**Tabel: `posApp_sales`**
| Kolom | Tipe | Catatan |
|---|---|---|
| `id` | BigAutoField PK | |
| `code` | CharField(10) | Format: `TAHUN` + 5 digit urut (mis. `202500001`) |
| `sub_total` | FloatField | Total sebelum diskon |
| `diskon` | FloatField | Diskon dalam % |
| `diskon_amount` | FloatField | Nilai nominal diskon (Rp) |
| `grand_total` | FloatField | Total akhir |
| `tendered_amount` | FloatField | Jumlah dibayar pelanggan |
| `amount_change` | FloatField | Kembalian |
| `payment_method` | CharField(50) | `Tunai` / `QRIS` / `Transfer` |
| `customer_name` | CharField(50) | nullable |
| `customer_wa` | CharField(15) | nullable |
| `customer_address` | CharField(50) | nullable |
| `cashier` | FK → auth_user | SET_NULL, nullable |
| `date_added` | DateTimeField | default=now |
| `date_updated` | DateTimeField | auto_now |

**Tabel: `posApp_salesitems`**
| Kolom | Tipe | Catatan |
|---|---|---|
| `id` | BigAutoField PK | |
| `sale_id` | FK → sales | CASCADE |
| `product_id` | FK → products | CASCADE |
| `price` | FloatField | Harga saat transaksi |
| `qty` | FloatField | Jumlah unit |
| `total` | FloatField | `price × qty` |

---

### 6. Riwayat Penjualan

#### `GET /sales` — Daftar Transaksi
Tabel: Kode · Pelanggan · Kasir · Metode Bayar · Total · Diskon · Tanggal
Aksi: Lihat Struk (semua), Hapus (Admin)

**Hapus Transaksi:** stok produk dikembalikan otomatis (`stock += qty`) + **[INVENTORY]** log `MASUK` (retur balik) dicatat ke `posApp_inventorylog`

#### Modal Receipt (`GET /receipt?id=<id>`)
- Detail transaksi: kode, tanggal, kasir, pelanggan
- Tabel item: Nama, Qty, Harga, Subtotal
- Ringkasan: Subtotal, Diskon, Total, Bayar, Kembalian
- Tombol Cetak

---

### 7. Inventory ⬅ MODUL BARU

#### `GET /inventory` — Log Pergerakan Stok (Semua Produk)

**Filter:**
- Dropdown Produk
- Dropdown Jenis: Semua / MASUK / KELUAR / PENYESUAIAN
- Rentang Tanggal (dari — hingga)

**Ringkasan Banner:**
- Total Masuk periode ini · Total Keluar periode ini · Jumlah Produk Stok Menipis (≤5)

**Tabel Log:**
| Kolom | Keterangan |
|---|---|
| Tanggal | Waktu kejadian |
| Produk | Nama + Kode SKU |
| Jenis | 🟢 MASUK · 🔴 KELUAR · 🟡 PENYESUAIAN |
| Jumlah | `+5` atau `-1` |
| Stok Sebelum | Snapshot stok sebelum kejadian |
| Stok Sesudah | Snapshot stok setelah kejadian |
| Referensi | Kode transaksi POS atau `—` jika manual |
| Keterangan | Catatan (mis. "Pembelian Baru", "Terjual via POS") |
| Dicatat Oleh | Username pengguna |

---

#### `GET/POST /inventory/add` — Tambah Stok Masuk *(Admin only)*

Field form:
- **Produk** (dropdown — tampilkan stok saat ini)
- **Jumlah** (angka positif)
- **Jenis Masuk:** Pembelian Baru / Retur dari Pelanggan / Koreksi / Stok Awal
- **Harga Beli/Unit** (opsional, untuk info modal)
- **Keterangan** (teks bebas)
- **Tanggal** (default hari ini)

Yang terjadi saat disimpan:
1. `product.stock += jumlah`
2. Catat log `MASUK` ke `posApp_inventorylog`

---

#### `GET/POST /inventory/adjust` — Penyesuaian Stok *(Admin only)*

Field form:
- **Produk** (dropdown)
- **Stok Sistem** (read-only, otomatis terisi)
- **Stok Fisik Sebenarnya** (input hasil hitung fisik)
- **Selisih** (dihitung otomatis: `fisik - sistem`, tampilkan hijau/merah)
- **Keterangan** (wajib diisi)

Yang terjadi saat disimpan:
1. `product.stock = stok_fisik`
2. Catat log `PENYESUAIAN` ke `posApp_inventorylog` dengan `quantity_change = selisih`

---

#### `GET /inventory/product/<id>` — Detail Stok per Produk

- **Header:** Foto, Nama, SKU, Merek, **Stok Saat Ini** (badge warna), Garansi
- **Grafik:** Tren jumlah stok dari waktu ke waktu (line chart)
- **Tabel Histori:** sama seperti halaman log utama, tapi hanya untuk produk ini

---

#### `GET /inventory/low-stock` — Produk Stok Menipis

Menampilkan produk dengan `stock ≤ 5`.

Tabel: Foto · SKU · Nama · Merek · **Stok** (badge merah) · Tombol "Catat Stok Masuk"

---

#### Tabel: `posApp_inventorylog` *(BARU)*

| Kolom | Tipe | Catatan |
|---|---|---|
| `id` | BigAutoField PK | |
| `product` | FK → products | CASCADE |
| `movement_type` | CharField(20) | `MASUK` / `KELUAR` / `PENYESUAIAN` |
| `quantity_change` | IntegerField | Positif=masuk, Negatif=keluar |
| `stock_before` | IntegerField | Snapshot stok sebelum |
| `stock_after` | IntegerField | Snapshot stok sesudah |
| `reference_code` | CharField(20) | Kode transaksi POS (nullable) |
| `note` | TextField | Keterangan / catatan |
| `buy_price` | FloatField | Harga beli/unit (nullable, khusus MASUK) |
| `recorded_by` | FK → auth_user | SET_NULL, nullable |
| `date_added` | DateTimeField | default=now |

---

## Integrasi Inventory (Otomatis)

| Trigger | Aksi ke Inventory |
|---|---|
| Transaksi POS selesai | Log `KELUAR` per item, `reference_code` = kode transaksi |
| Hapus transaksi | Log `MASUK` per item (retur), note = "Pengembalian dari hapus transaksi [kode]" |
| Admin catat stok masuk | Log `MASUK` dengan jenis & keterangan yang dipilih |
| Admin sesuaikan stok | Log `PENYESUAIAN` dengan nilai selisih |

---

## URL Lengkap Sistem

| URL | Fungsi | Akses |
|---|---|---|
| `/login` | Login | Public |
| `/logout` | Logout | Login |
| `/` | Dashboard | Login |
| `/category` | Daftar Kategori | Login |
| `/manage_category` | Form Kategori | Admin |
| `/save_category` | Simpan Kategori (POST) | Admin |
| `/delete_category` | Hapus Kategori (POST) | Admin |
| `/products` | Daftar Produk | Login |
| `/manage_products` | Form Produk | Admin |
| `/save_product` | Simpan Produk (POST) | Admin |
| `/delete_product` | Hapus Produk (POST) | Admin |
| `/pos` | Halaman Kasir | Login |
| `/checkout-modal` | Modal Checkout | Login |
| `/save-pos` | Simpan Transaksi (POST) | Login |
| `/sales` | Riwayat Penjualan | Login |
| `/receipt` | Struk Transaksi | Login |
| `/delete_sale` | Hapus Transaksi (POST) | Admin |
| `/check-new-sales/` | Polling notifikasi (AJAX) | Login |
| `/inventory` | Log Pergerakan Stok | Login | ⬅ BARU |
| `/inventory/add` | Tambah Stok Masuk | Admin | ⬅ BARU |
| `/inventory/adjust` | Penyesuaian Stok | Admin | ⬅ BARU |
| `/inventory/product/<id>` | Detail Stok Produk | Login | ⬅ BARU |
| `/inventory/low-stock` | Produk Stok Menipis | Login | ⬅ BARU |
| `/admin` | Django Admin Panel | Admin | |

---

## Relasi Database

```
auth_user
  ├── posApp_sales.cashier (FK)
  └── posApp_inventorylog.recorded_by (FK)

posApp_category
  ├── posApp_categorytype.category (FK)
  └── posApp_products.category_id (FK)

posApp_products
  ├── posApp_salesitems.product_id (FK)
  └── posApp_inventorylog.product (FK)

posApp_sales
  └── posApp_salesitems.sale_id (FK)

posApp_inventorylog.reference_code → posApp_sales.code (referensi lunak)
```
