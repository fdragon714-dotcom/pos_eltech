"""
Script: Reset Semua Data Penjualan
Tujuan:
  - Hapus semua transaksi penjualan (Sales + salesItems)
  - Hapus semua InventoryLog yang berasal dari penjualan (KELUAR) dan pengembalian (Pengembalian dari hapus)
  - Hapus data test yang dibuat oleh test_delete.py (produk "Test Prod", kategori "Test Cat")
  - Perbaiki stok produk yang negatif menjadi 0
  - Tidak menyentuh log MASUK yang diinput manual
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pos.settings")
django.setup()

from posApp.models import Sales, salesItems, InventoryLog, Products, Category

print("=" * 60)
print("RESET DATA PENJUALAN")
print("=" * 60)

# 1. Hapus semua InventoryLog dari penjualan POS (KELUAR)
keluar_logs = InventoryLog.objects.filter(movement_type='KELUAR')
keluar_count = keluar_logs.count()
keluar_logs.delete()
print(f"[OK] Hapus {keluar_count} log KELUAR (dari POS)")

# 2. Hapus semua InventoryLog pengembalian dari delete_sale
balik_logs = InventoryLog.objects.filter(note__startswith='Pengembalian dari hapus transaksi')
balik_count = balik_logs.count()
balik_logs.delete()
print(f"[OK] Hapus {balik_count} log MASUK pengembalian (dari hapus transaksi)")

# 3. Hapus semua Sales dan salesItems (cascade)
sales_count = Sales.objects.count()
Sales.objects.all().delete()
print(f"[OK] Hapus {sales_count} transaksi penjualan (Sales)")

# 4. Hapus data test dari test_delete.py
test_cat = Category.objects.filter(name='Test Cat').first()
if test_cat:
    test_prod = Products.objects.filter(name='Test Prod', category_id=test_cat).first()
    if test_prod:
        # Hapus log inventory test juga
        InventoryLog.objects.filter(product=test_prod).delete()
        test_prod.delete()
        print("[OK] Hapus produk test 'Test Prod'")
    test_cat.delete()
    print("[OK] Hapus kategori test 'Test Cat'")
else:
    print("[--] Tidak ada data test yang perlu dihapus")

# 5. Perbaiki stok produk yang bernilai negatif
negative_products = Products.objects.filter(stock__lt=0)
neg_count = negative_products.count()
if neg_count > 0:
    for p in negative_products:
        print(f"[WARN] Produk '{p.name}' stok = {p.stock} -> direset ke 0")
        p.stock = 0
        p.save()
    print(f"[OK] Reset {neg_count} produk dengan stok negatif menjadi 0")
else:
    print("[OK] Tidak ada produk dengan stok negatif")

# 6. Tampilkan ringkasan akhir
print()
print("=" * 60)
print("RINGKASAN AKHIR")
print("=" * 60)
print(f"Total Transaksi Penjualan  : {Sales.objects.count()}")
print(f"Total Log Inventory MASUK  : {InventoryLog.objects.filter(movement_type='MASUK').count()}")
print(f"Total Log Inventory KELUAR : {InventoryLog.objects.filter(movement_type='KELUAR').count()}")
print(f"Produk Stok Negatif        : {Products.objects.filter(stock__lt=0).count()}")
print()
print("Daftar Produk & Stok Saat Ini:")
for p in Products.objects.filter(status=1).order_by('name'):
    print(f"  [{p.code}] {p.name} | Stok: {p.stock}")
print()
print("SELESAI. Data penjualan sudah direset.")
