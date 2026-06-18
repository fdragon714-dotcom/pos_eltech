import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pos.settings")
django.setup()

from posApp.models import Sales, salesItems

try:
    # Just a test filter
    res = salesItems.objects.filter(sale_id='1')
    print("Filter succeeded, count:", res.count())
except Exception as e:
    print("Exception:", e)
