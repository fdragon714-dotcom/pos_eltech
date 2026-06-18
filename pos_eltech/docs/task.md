# Task — Implementasi Modul Inventory
> Berdasarkan PRD v2.0 | Project: `pos_eltech`

---

## Status Project Saat Ini (Sudah Ada ✅)

Semua modul di bawah ini sudah **selesai** dan berfungsi:

- ✅ Login / Logout
- ✅ Dashboard dengan grafik, filter periode, top produk, indikator growth
- ✅ CRUD Kategori & Tipe Merek
- ✅ CRUD Produk (stok, garansi, foto)
- ✅ Halaman POS / Kasir (keranjang, diskon, checkout, QRIS)
- ✅ Pemotongan stok otomatis saat transaksi POS
- ✅ Riwayat Penjualan + struk/receipt
- ✅ Pengembalian stok saat hapus transaksi
- ✅ AJAX polling notifikasi transaksi baru
- ✅ Django Unfold Admin Panel

---

## Yang Belum Ada & Perlu Diimplementasikan

---

### A. Database — Model Baru

- [ ] **Buat model `InventoryLog`** di `posApp/models.py`
  - Field: `product` (FK Products), `movement_type` (CharField: MASUK/KELUAR/PENYESUAIAN), `quantity_change` (IntegerField), `stock_before` (IntegerField), `stock_after` (IntegerField), `reference_code` (CharField nullable), `note` (TextField), `buy_price` (FloatField nullable), `recorded_by` (FK User, SET_NULL nullable), `date_added` (DateTimeField default=now)
- [x] **Jalankan migrasi** (`makemigrations` + `migrate`)

---

### B. Integrasi Otomatis ke Modul yang Sudah Ada

- [x] **`save_pos` (views.py)** — Setelah stok dikurangi, tambahkan pencatatan log `KELUAR` ke `InventoryLog` per item:
  - `stock_before` = stok sebelum dikurangi
  - `stock_after` = stok setelah dikurangi
  - `reference_code` = kode transaksi (`sales.code`)
  - `note` = "Terjual via POS"
  - `recorded_by` = `request.user`

- [x] **`delete_sale` (views.py)** — Setelah stok dikembalikan, tambahkan pencatatan log `MASUK` ke `InventoryLog` per item:
  - `stock_before` = stok sebelum dikembalikan
  - `stock_after` = stok setelah dikembalikan
  - `reference_code` = kode transaksi yang dihapus
  - `note` = f"Pengembalian dari hapus transaksi {kode}"
  - `recorded_by` = `request.user`

- [x] **Validasi stok di `save_pos`** — Cek sebelum menyimpan: jika `product.stock - qty < 0`, return error JSON `{"status": "failed", "msg": "Stok [nama produk] tidak cukup"}` dan batalkan transaksi

---

### C. Views Baru — `posApp/views.py`

- [x] **`inventory_list`** → `GET /inventory`
  - Query semua `InventoryLog` dengan filter: produk (opsional), jenis (opsional), rentang tanggal (opsional)
  - Hitung ringkasan: total masuk, total keluar, jumlah produk stok ≤ 5
  - Kirim ke template `inventory.html`

- [x] **`inventory_add`** → `GET/POST /inventory/add` *(Admin only)*
  - GET: render form dengan dropdown semua produk aktif
  - POST: ambil produk, simpan `stock_before`, update `product.stock += jumlah`, simpan `stock_after`, catat `InventoryLog` tipe `MASUK`

- [x] **`inventory_adjust`** → `GET/POST /inventory/adjust` *(Admin only)*
  - GET: render form
  - POST: ambil produk & stok fisik, hitung selisih (`fisik - sistem`), update `product.stock = stok_fisik`, catat `InventoryLog` tipe `PENYESUAIAN`

- [x] **`inventory_product`** → `GET /inventory/product/<id>`
  - Query `InventoryLog` berdasarkan `product_id`
  - Kirim data produk + histori log ke template `inventory_product.html`

- [x] **`inventory_low_stock`** → `GET /inventory/low-stock`
  - Query `Products.objects.filter(stock__lte=5, status=1)`
  - Kirim ke template `inventory_low_stock.html`

---

### D. URL Baru — `posApp/urls.py`

- [x] Tambahkan 5 URL baru:
  ```python
  path('inventory', views.inventory_list, name='inventory-page'),
  path('inventory/add', views.inventory_add, name='inventory-add'),
  path('inventory/adjust', views.inventory_adjust, name='inventory-adjust'),
  path('inventory/product/<int:id>', views.inventory_product, name='inventory-product'),
  path('inventory/low-stock', views.inventory_low_stock, name='inventory-low-stock'),
  ```

---

### E. Template Baru — `posApp/templates/posApp/`

- [x] **`inventory.html`** — Halaman Log Pergerakan Stok
  - Banner ringkasan: Total Masuk · Total Keluar · Stok Menipis
  - Form filter: dropdown Produk, dropdown Jenis, input rentang tanggal
  - Tabel: Tanggal · Produk · Jenis (badge warna) · Jumlah (+/-) · Stok Sebelum · Stok Sesudah · Referensi · Keterangan · Dicatat Oleh

- [x] **`inventory_add.html`** — Form Tambah Stok Masuk
  - Dropdown Produk (tampilkan stok saat ini)
  - Input: Jumlah, Jenis Masuk (dropdown), Harga Beli/Unit (opsional), Keterangan, Tanggal

- [x] **`inventory_adjust.html`** — Form Penyesuaian Stok
  - Dropdown Produk
  - Stok Sistem (read-only, diisi JS saat produk dipilih)
  - Input Stok Fisik
  - Selisih (dihitung otomatis JS, tampilkan hijau/merah)
  - Input Keterangan (wajib)

- [x] **`inventory_product.html`** — Detail Stok per Produk
  - Header: foto, nama, SKU, merek, badge stok, garansi
  - Line chart tren stok dari waktu ke waktu
  - Tabel histori log khusus produk ini

- [x] **`inventory_low_stock.html`** — Produk Stok Menipis
  - Tabel: Foto · SKU · Nama · Merek · Stok (badge merah) · Tombol "Catat Stok Masuk"

---

### F. Navigasi — `navigation.html`

- [x] Tambahkan menu **Inventory** di sidebar dengan ikon `inventory` (Material Icons):
  ```html
  <div class="mdc-list-item mdc-drawer-item">
      <a class="mdc-drawer-link" href="{% url 'inventory-page' %}">
          <i class="material-icons mdc-drawer-item-icon">inventory</i>
          <span>Inventory</span>
      </a>
  </div>
  ```
  - Tempatkan di antara menu "Daftar Produk" dan "Penjualan"

---

### G. Django Admin Panel — `admin.py`

- [x] Register model `InventoryLog` ke admin dengan `ModelAdmin` (Unfold):
  - `list_display`: Tanggal, Produk, Jenis (badge), Jumlah, Stok Sebelum, Stok Sesudah, Referensi, Dicatat Oleh
  - `list_filter`: `movement_type`, `date_added`, `product`
  - `search_fields`: `product__name`, `product__code`, `reference_code`
  - `readonly_fields`: semua field (log tidak boleh diedit manual dari admin)
  - `ordering`: `-date_added`

- [x] Tambahkan entri `InventoryLog` ke sidebar Unfold di `settings.py`:
  ```python
  {
      "title": "Log Inventory",
      "icon": "inventory",
      "link": reverse_lazy("admin:posApp_inventorylog_changelist"),
  }
  ```
  Tempatkan di grup "Manajemen Toko"

---

### H. Impor Model di Views

- [x] Update baris impor di `views.py`:
  ```python
  from posApp.models import Category, Products, Sales, salesItems, InventoryLog
  ```

---

## Urutan Pengerjaan yang Disarankan

1. **A** — Buat model + migrasi (fondasi data)
2. **H** — Update impor di views.py
3. **B** — Integrasi otomatis ke `save_pos` & `delete_sale` + validasi stok
4. **D** — Daftarkan URL baru
5. **C** — Buat semua views baru
6. **E** — Buat semua template baru
7. **F** — Tambah menu navigasi sidebar
8. **G** — Register ke Django Admin

---

### I. Tambahan Fitur Edit Stok Masuk (Berdasarkan Permintaan User)

- [x] Tambah tombol Edit & Delete pada `inventory.html` khusus baris `MASUK`
- [x] Buat modal UI edit: `inventory_edit_masuk.html`
- [x] Tambah fungsi `inventory_edit_masuk` di `views.py` (Koreksi stok + selisih)
- [x] Tambah fungsi `inventory_delete_masuk` di `views.py` (Koreksi kembalikan stok)
- [x] Daftarkan rute di `urls.py`
