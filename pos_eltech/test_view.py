import os
import django
from django.test.client import RequestFactory
from django.contrib.auth.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pos.settings")
django.setup()

from posApp.models import Sales, salesItems, Products
from posApp.views import delete_sale

sale = Sales.objects.last()
if not sale:
    print("No sales in database.")
else:
    print("Found sale:", sale.id)
    items = salesItems.objects.filter(sale_id=sale.id)
    for i in items:
        print("Item product:", i.product_id.name, "Qty:", i.qty, "Stock before:", i.product_id.stock)
        
    factory = RequestFactory()
    request = factory.post('/delete_sale', {'id': sale.id})
    # Mock user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    request.user = user
    
    response = delete_sale(request)
    print("Response status_code:", response.status_code)
    print("Response content:", response.content)
    
    for i in items:
        # Refresh from db
        prod = Products.objects.get(id=i.product_id.id)
        print("Item product:", prod.name, "Stock after:", prod.stock)
