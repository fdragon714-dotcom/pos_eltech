from datetime import datetime
from unicodedata import category
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

# class Employees(models.Model):
#     code = models.CharField(max_length=100,blank=True) 
#     firstname = models.TextField() 
#     middlename = models.TextField(blank=True,null= True) 
#     lastname = models.TextField() 
#     gender = models.TextField(blank=True,null= True) 
#     dob = models.DateField(blank=True,null= True) 
#     contact = models.TextField() 
#     address = models.TextField() 
#     email = models.TextField() 
#     department_id = models.ForeignKey(Department, on_delete=models.CASCADE) 
#     position_id = models.ForeignKey(Position, on_delete=models.CASCADE) 
#     date_hired = models.DateField() 
#     salary = models.FloatField(default=0) 
#     status = models.IntegerField() 
#     date_added = models.DateTimeField(default=timezone.now) 
#     date_updated = models.DateTimeField(auto_now=True) 

    # def __str__(self):
    #     return self.firstname + ' ' +self.middlename + ' '+self.lastname + ' '
    
    
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    status = models.IntegerField(default=1) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = "Merek & Kategori"
        verbose_name_plural = "Daftar Merek"

    def __str__(self):
        return self.name

class CategoryType(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='type_images/', null=True, blank=True)

    class Meta:
        verbose_name = "Tipe Merek"
        verbose_name_plural = "Daftar Tipe Merek"

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Products(models.Model):
    code = models.CharField(max_length=10)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.TextField()
    price = models.FloatField(default=0)
    status = models.IntegerField(default=1) 
    
    # ==========================================
    # TAMBAHAN KOLOM STOK & GAMBAR UNTUK PRODUK
    # ==========================================
    stock = models.IntegerField(default=0, null=True, blank=True) # <-- Dibuat aman dari nilai kosong
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    # ==========================================
    
    # ==========================================
    # TAMBAHAN KOLOM GARANSI (ANTI-ERROR)
    # ==========================================
    warranty = models.IntegerField(default=0, null=True, blank=True) 
    # ==========================================

    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = "Katalog Produk"
        verbose_name_plural = "Daftar Produk"

    def __str__(self):
        return self.code + " - " + self.name

class Sales(models.Model):
    code = models.CharField(max_length=10)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    diskon_amount = models.FloatField(default=0)
    diskon = models.FloatField(default=0)
    tendered_amount = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    
    # ==========================================
    # TAMBAHAN KOLOM METODE PEMBAYARAN
    # ==========================================
    payment_method = models.CharField(max_length=50, default='Tunai') 
    # ==========================================
    
    # ==========================================
    # WADAH BARU UNTUK DATA PELANGGAN
    # ==========================================
    customer_name = models.CharField(max_length=50, blank=True, null=True)
    customer_wa = models.CharField(max_length=15, blank=True, null=True)
    customer_address = models.CharField(max_length=50, blank=True, null=True)
    # ==========================================

    # ==========================================
    # KASIR YANG MEMPROSES
    # ==========================================
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # ==========================================

    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = "Riwayat Penjualan"
        verbose_name_plural = "Data Penjualan"

    def __str__(self):
        return self.code

class salesItems(models.Model):
    sale_id = models.ForeignKey(Sales,on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products,on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0)
    total = models.FloatField(default=0)

    class Meta:
        verbose_name = "Item Terjual"
        verbose_name_plural = "Detail Item Terjual"

class InventoryLog(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20) # MASUK, KELUAR, PENYESUAIAN
    quantity_change = models.IntegerField()
    stock_before = models.IntegerField()
    stock_after = models.IntegerField()
    reference_code = models.CharField(max_length=20, null=True, blank=True)
    note = models.TextField()
    buy_price = models.FloatField(null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Log Inventory"
        verbose_name_plural = "Log Inventory"

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity_change})"