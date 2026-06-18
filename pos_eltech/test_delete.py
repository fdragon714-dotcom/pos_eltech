import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pos.settings")
django.setup()

from posApp.models import Sales, salesItems, Products, Category

# Create dummy category
cat, _ = Category.objects.get_or_create(name="Test Cat", description="Test")
prod, _ = Products.objects.get_or_create(code="123", name="Test Prod", category_id=cat, price=100)
prod.stock = 10
prod.save()

# Create sale
sale = Sales.objects.create(code="S001")
item = salesItems.objects.create(sale_id=sale, product_id=prod, qty=2, price=100, total=200)

print("Before delete:")
print("Product stock:", Products.objects.get(id=prod.id).stock)

# Simulate delete_sale
id = str(sale.id)

sale_items = salesItems.objects.filter(sale_id=id)
print("Sale items count:", sale_items.count())

for item in sale_items:
    product = item.product_id
    if product:
        stock_before = product.stock
        product.stock += int(float(item.qty))
        product.save()

Sales.objects.filter(id=id).delete()

print("After delete:")
print("Product stock:", Products.objects.get(id=prod.id).stock)

