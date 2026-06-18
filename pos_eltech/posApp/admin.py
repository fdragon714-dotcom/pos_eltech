from django.contrib import admin
from django.utils.html import format_html
from django.utils.formats import number_format
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

admin.site.unregister(User)
admin.site.unregister(Group)

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].max_length = 20
            self.fields['username'].widget.attrs['maxlength'] = 20
            self.fields['username'].help_text = "Maksimal 20 karakter. Hanya huruf, angka, dan @/./+/-/_."
        if 'email' in self.fields:
            self.fields['email'].max_length = 30
            self.fields['email'].widget.attrs['maxlength'] = 30
            self.fields['email'].help_text = "Maksimal 30 karakter."
        if 'first_name' in self.fields:
            self.fields['first_name'].max_length = 30
            self.fields['first_name'].widget.attrs['maxlength'] = 30
            self.fields['first_name'].help_text = "Maksimal 30 karakter."
        if 'last_name' in self.fields:
            self.fields['last_name'].max_length = 30
            self.fields['last_name'].widget.attrs['maxlength'] = 30
            self.fields['last_name'].help_text = "Maksimal 30 karakter."

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].max_length = 20
            self.fields['username'].widget.attrs['maxlength'] = 20
            self.fields['username'].help_text = "Maksimal 20 karakter. Hanya huruf, angka, dan @/./+/-/_."
        if 'email' in self.fields:
            self.fields['email'].max_length = 30
            self.fields['email'].widget.attrs['maxlength'] = 30
            self.fields['email'].help_text = "Maksimal 30 karakter."
        if 'first_name' in self.fields:
            self.fields['first_name'].max_length = 30
            self.fields['first_name'].widget.attrs['maxlength'] = 30
            self.fields['first_name'].help_text = "Maksimal 30 karakter."
        if 'last_name' in self.fields:
            self.fields['last_name'].max_length = 30
            self.fields['last_name'].widget.attrs['maxlength'] = 30
            self.fields['last_name'].help_text = "Maksimal 30 karakter."

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

from posApp.models import Category, CategoryType, Products, Sales, salesItems, InventoryLog


# ─────────────────────────────────────────────────────────
#  Environment Badge (ditampilkan di header sidebar)
# ─────────────────────────────────────────────────────────
def environment_callback(request):
    return ["Development", "warning"]  # bisa diganti "Production", "danger"


# ─────────────────────────────────────────────────────────
#  INLINE: Tipe Merek (tampil di dalam form Merek)
# ─────────────────────────────────────────────────────────
class CategoryTypeInline(TabularInline):
    model = CategoryType
    extra = 1
    fields = ("name", "image")


# ─────────────────────────────────────────────────────────
#  INLINE: Item Terjual (tampil di dalam form Penjualan)
# ─────────────────────────────────────────────────────────
class salesItemsInline(TabularInline):
    model = salesItems
    extra = 0
    readonly_fields = ("product_id", "price", "qty", "total")
    fields = ("product_id", "price", "qty", "total")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────────────────
#  MEREK & KATEGORI
# ─────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display   = ("preview_image", "name", "description_short", "status_badge", "date_added")
    list_display_links = ("name",)
    list_filter    = ("status",)
    search_fields  = ("name",)
    ordering       = ("name",)
    inlines        = [CategoryTypeInline]

    fieldsets = (
        ("Informasi Merek", {"fields": ("name", "description", "image")}),
        ("Status", {"fields": ("status",)}),
    )

    @admin.display(description="Foto")
    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:45px;object-fit:cover;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">',
                obj.image.url,
            )
        return format_html('<span style="color:#9ca3af;">{}</span>', '—')

    @admin.display(description="Deskripsi")
    def description_short(self, obj):
        return obj.description[:60] + "…" if len(obj.description) > 60 else obj.description

    @display(description="Status", label=True)
    def status_badge(self, obj):
        if obj.status == 1:
            return "Aktif", "success"
        return "Nonaktif", "danger"


# ─────────────────────────────────────────────────────────
#  TIPE MEREK (standalone)
# ─────────────────────────────────────────────────────────
@admin.register(CategoryType)
class CategoryTypeAdmin(ModelAdmin):
    list_display  = ("name", "category")
    list_filter   = ("category",)
    search_fields = ("name", "category__name")
    ordering      = ("category", "name")


# ─────────────────────────────────────────────────────────
#  PRODUK
# ─────────────────────────────────────────────────────────
@admin.register(Products)
class ProductsAdmin(ModelAdmin):
    list_display   = (
        "preview_image", "code", "name", "category_id",
        "formatted_price", "stock_badge", "warranty_badge", "status_badge",
    )
    list_display_links = ("code", "name")
    list_filter    = ("status", "category_id")
    search_fields  = ("code", "name", "description")
    ordering       = ("category_id", "name")
    list_per_page  = 20

    fieldsets = (
        ("Identitas Produk", {
            "fields": ("code", "name", "category_id", "description"),
        }),
        ("Harga & Stok", {
            "fields": ("price", "stock", "warranty"),
        }),
        ("Media & Status", {
            "fields": ("image", "status"),
        }),
    )

    @admin.display(description="Foto")
    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:42px;height:42px;object-fit:cover;border-radius:8px;">',
                obj.image.url,
            )
        return format_html('<span style="color:#9ca3af;">{}</span>', '—')

    @admin.display(description="Harga", ordering="price")
    def formatted_price(self, obj):
        return "Rp {:,.0f}".format(obj.price).replace(",", ".")

    @display(description="Stok", ordering="stock", label=True)
    def stock_badge(self, obj):
        stok = obj.stock or 0
        if stok > 10:
            return str(stok), "success"
        elif stok > 0:
            return str(stok), "warning"
        return str(stok), "danger"

    @display(description="Garansi", label=True)
    def warranty_badge(self, obj):
        hari = obj.warranty or 0
        if hari > 0:
            return f"{hari} Hari", "info"
        return "Non-Garansi", "warning"

    @display(description="Status", label=True)
    def status_badge(self, obj):
        if obj.status == 1:
            return "Aktif", "success"
        return "Arsip", "warning"


# ─────────────────────────────────────────────────────────
#  PENJUALAN
# ─────────────────────────────────────────────────────────
@admin.register(Sales)
class SalesAdmin(ModelAdmin):
    list_display   = (
        "code", "formatted_grand_total", "payment_badge",
        "customer_info", "discount_info", "date_added",
    )
    list_display_links = ("code",)
    list_filter    = ("payment_method", "date_added")
    search_fields  = ("code", "customer_name", "customer_wa")
    ordering       = ("-date_added",)
    readonly_fields = (
        "code", "sub_total", "grand_total", "diskon_amount", "diskon",
        "tendered_amount", "amount_change", "date_added", "date_updated",
    )
    inlines        = [salesItemsInline]
    list_per_page  = 25
    date_hierarchy = "date_added"

    fieldsets = (
        ("Info Transaksi", {
            "fields": ("code", "date_added", "payment_method"),
        }),
        ("Rincian Pembayaran", {
            "fields": (
                "sub_total", "diskon", "diskon_amount",
                "grand_total", "tendered_amount", "amount_change",
            ),
        }),
        ("Data Pelanggan", {
            "fields": ("customer_name", "customer_wa", "customer_address"),
        }),
    )

    @admin.display(description="Total Akhir", ordering="grand_total")
    def formatted_grand_total(self, obj):
        formatted_val = "{:,.0f}".format(obj.grand_total).replace(",", ".")
        return format_html(
            '<span style="font-weight:700;color:#166534;">Rp {}</span>', formatted_val
        )

    @display(description="Metode Bayar", label=True)
    def payment_badge(self, obj):
        method = obj.payment_method or "Tunai"
        if method == "Tunai":
            return method, "success"
        elif method == "QRIS":
            return method, "info"
        elif method == "Transfer":
            return method, "warning"
        return method, "success"

    @admin.display(description="Pelanggan")
    def customer_info(self, obj):
        if obj.customer_name:
            return format_html(
                '<span style="font-weight:600;">{}</span>'
                '<br><span style="color:#6b7280;font-size:0.75rem;">{}</span>',
                obj.customer_name,
                obj.customer_wa or "—",
            )
        return format_html('<span style="color:#9ca3af;">{}</span>', 'Umum')

    @admin.display(description="Diskon")
    def discount_info(self, obj):
        if obj.diskon and obj.diskon > 0:
            formatted_amount = "{:,.0f}".format(obj.diskon_amount).replace(",", ".")
            return format_html(
                '<span style="color:#dc2626;font-weight:600;">{}%</span>'
                '<br><span style="color:#6b7280;font-size:0.75rem;">Rp {}</span>',
                int(obj.diskon),
                formatted_amount
            )
        return format_html('<span style="color:#9ca3af;">{}</span>', '—')


# ─────────────────────────────────────────────────────────
#  DETAIL ITEM TERJUAL (standalone, read-only)
# ─────────────────────────────────────────────────────────
@admin.register(salesItems)
class salesItemsAdmin(ModelAdmin):
    list_display  = ("sale_id", "product_id", "formatted_price", "qty", "formatted_total")
    list_filter   = ("sale_id",)
    search_fields = ("sale_id__code", "product_id__name")
    ordering      = ("-sale_id__date_added",)
    readonly_fields = ("sale_id", "product_id", "price", "qty", "total")
    list_per_page = 30

    def has_add_permission(self, request):
        return False

    @admin.display(description="Harga/Unit")
    def formatted_price(self, obj):
        return "Rp {:,.0f}".format(obj.price).replace(",", ".")

    @admin.display(description="Total")
    def formatted_total(self, obj):
        formatted_val = "{:,.0f}".format(obj.total).replace(",", ".")
        return format_html(
            '<span style="font-weight:600;">Rp {}</span>', formatted_val
        )

# ─────────────────────────────────────────────────────────
#  LOG INVENTORY (Read-only)
# ─────────────────────────────────────────────────────────
@admin.register(InventoryLog)
class InventoryLogAdmin(ModelAdmin):
    list_display = ("date_added", "product", "movement_badge", "quantity_change", "stock_before", "stock_after", "reference_code", "recorded_by")
    list_display_links = ("date_added", "product")
    list_filter = ("movement_type", "date_added", "product")
    search_fields = ("product__name", "product__code", "reference_code")
    readonly_fields = [f.name for f in InventoryLog._meta.fields if f.name != 'id']
    ordering = ("-date_added",)
    list_per_page = 25

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    @display(description="Jenis", label=True)
    def movement_badge(self, obj):
        if obj.movement_type == "MASUK":
            return "MASUK", "success"
        elif obj.movement_type == "KELUAR":
            return "KELUAR", "danger"
        return "PENYESUAIAN", "warning"
