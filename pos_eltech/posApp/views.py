from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.http import JsonResponse
from posApp.models import Category, Products, Sales, salesItems, InventoryLog
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
import json, sys, calendar
from datetime import date, datetime, timedelta

# ==========================================
# SATPAM PENGECEK HAK AKSES (HANYA BOS)
# ==========================================
def is_admin(user):
    return user.is_superuser

# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    from django.utils import timezone
    date_param = request.GET.get('date')
    if date_param:
        try:
            if len(date_param) > 10:
                now_unaware = datetime.strptime(date_param, "%Y-%m-%d %H:%M")
            else:
                now_unaware = datetime.strptime(date_param, "%Y-%m-%d")
            now = timezone.make_aware(now_unaware)
        except ValueError:
            now = timezone.localtime(timezone.now())
    else:
        now = timezone.localtime(timezone.now())

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    yesterday_start = today_start - timedelta(days=1)
    
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    
    # 1. Statistik Dasar
    categories = Category.objects.all().count() 
    products = Products.objects.all().count()   
    
    month_start = today_start.replace(day=1)
    if month_start.month == 12:
        next_month_start = month_start.replace(year=month_start.year+1, month=1)
    else:
        next_month_start = month_start.replace(month=month_start.month+1)
        
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    
    # =======================================================
    # 2. LOGIKA GRAFIK SAHAM DINAMIS & STATISTIK KARTU
    # =======================================================
    filter_chart = request.GET.get('filter_chart', 'bulan_ini')
    sales_dates = []
    sales_amounts = []
    chart_title = ""
    selected_period_name = ""
    transaction = 0

    if filter_chart == 'hari_ini':
        selected_period_name = f"Hari Ini ({now.strftime('%d %b %Y')})"
        chart_title = f"Periode Hari Ini ({now.strftime('%d %b %Y')})"
        sales_today_list = list(Sales.objects.filter(date_added__gte=today_start, date_added__lt=today_end))
        transaction = len(sales_today_list)
        
        for h in range(0, 24):
            hourly_revenue = sum(s.grand_total for s in sales_today_list if timezone.localtime(s.date_added).hour == h)
            sales_dates.append(f"{h:02d}:00")
            sales_amounts.append(float(hourly_revenue))
            
        chart_total_val = sum(sales_amounts)
        
        yesterday_total_agg = Sales.objects.filter(date_added__gte=yesterday_start, date_added__lt=today_start).aggregate(Sum('grand_total'))['grand_total__sum']
        yesterday_total = float(yesterday_total_agg) if yesterday_total_agg else 0.0
        
        if yesterday_total > 0:
            chart_pct = ((chart_total_val - yesterday_total) / yesterday_total) * 100
        else:
            chart_pct = 100.0 if chart_total_val > 0 else 0.0

    elif filter_chart == 'minggu_ini':
        start_of_week = today_start - timedelta(days=today_start.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        
        selected_period_name = f"Minggu Ini ({start_of_week.strftime('%d %b')} - {(end_of_week - timedelta(days=1)).strftime('%d %b %Y')})"
        chart_title = f"Periode {selected_period_name}"
        
        sales_week_list = list(Sales.objects.filter(date_added__gte=start_of_week, date_added__lt=end_of_week))
        transaction = len(sales_week_list)
        
        for d in range(0, 7):
            target_date = start_of_week + timedelta(days=d)
            if target_date > today_start:
                break
                
            daily_revenue = sum(s.grand_total for s in sales_week_list if timezone.localtime(s.date_added).date() == target_date.date())
            
            day_names = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            sales_dates.append(f"{day_names[d]} {target_date.day}")
            sales_amounts.append(float(daily_revenue))
            
        chart_total_val = sum(sales_amounts)
        
        start_of_last_week = start_of_week - timedelta(days=7)
        
        last_week_total_agg = Sales.objects.filter(date_added__gte=start_of_last_week, date_added__lt=start_of_week).aggregate(Sum('grand_total'))['grand_total__sum']
        last_week_total = float(last_week_total_agg) if last_week_total_agg else 0.0
        
        if last_week_total > 0:
            chart_pct = ((chart_total_val - last_week_total) / last_week_total) * 100
        else:
            chart_pct = 100.0 if chart_total_val > 0 else 0.0

    elif filter_chart == 'tahun_ini':
        selected_period_name = f"Tahun Ini ({current_year})"
        chart_title = f"Periode {selected_period_name}"
        year_start = today_start.replace(month=1, day=1)
        next_year_start = year_start.replace(year=year_start.year+1)
        
        sales_year_list = list(Sales.objects.filter(date_added__gte=year_start, date_added__lt=next_year_start))
        transaction = len(sales_year_list)
        
        for m in range(1, int(current_month) + 1):
            monthly_revenue = sum(s.grand_total for s in sales_year_list if timezone.localtime(s.date_added).month == m)
            
            month_name = date(int(current_year), m, 1).strftime('%b')
            sales_dates.append(month_name)
            sales_amounts.append(float(monthly_revenue))
            
        chart_total_val = sum(sales_amounts)

        if len(sales_amounts) >= 2:
            first_val = sales_amounts[0]
            last_val = sales_amounts[-1]
            diff = last_val - first_val
            if first_val > 0:
                chart_pct = (diff / first_val) * 100
            else:
                chart_pct = 100.0 if diff > 0 else 0.0
        else:
            chart_pct = 0.0

    else:
        # Default: Bulan Ini
        selected_period_name = f"Bulan Ini ({now.strftime('%B %Y')})"
        chart_title = f"Periode {selected_period_name}"
        num_days = calendar.monthrange(int(current_year), int(current_month))[1]
        
        sales_month_list = list(Sales.objects.filter(date_added__gte=month_start, date_added__lt=next_month_start))
        transaction = len(sales_month_list)
        
        for d in range(1, num_days + 1):
            target_date = month_start.replace(day=d)
            if target_date > today_start: 
                break 
            
            daily_revenue = sum(s.grand_total for s in sales_month_list if timezone.localtime(s.date_added).day == d)
            
            sales_dates.append(f"{d} {now.strftime('%b')}")
            sales_amounts.append(float(daily_revenue))
            
        chart_total_val = sum(sales_amounts)
        
        rev_last_month_agg = Sales.objects.filter(date_added__gte=last_month_start, date_added__lt=month_start).aggregate(Sum('grand_total'))['grand_total__sum']
        rev_last_month = rev_last_month_agg if rev_last_month_agg else 0
        
        if rev_last_month > 0:
            chart_pct = ((chart_total_val - rev_last_month) / rev_last_month) * 100
        else:
            chart_pct = 100.0 if chart_total_val > 0 else 0.0

    chart_growth_pct = f"+{chart_pct:.2f}" if chart_pct > 0 else f"{chart_pct:.2f}"
    is_chart_positive = chart_pct >= 0


    # =======================================================
    # 3. PRODUK TERLARIS
    # =======================================================
    filter_terlaris = request.GET.get('filter_terlaris', 'hari_ini')
    qs_terlaris = salesItems.objects.all()

    if filter_terlaris == 'bulan_ini':
        qs_terlaris = qs_terlaris.filter(sale_id__date_added__gte=month_start, sale_id__date_added__lt=next_month_start)
    elif filter_terlaris == 'tahun_ini':
        year_start = today_start.replace(month=1, day=1)
        next_year_start = year_start.replace(year=year_start.year+1)
        qs_terlaris = qs_terlaris.filter(sale_id__date_added__gte=year_start, sale_id__date_added__lt=next_year_start)
    elif filter_terlaris == 'minggu_ini':
        start_of_week = today_start - timedelta(days=today_start.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        qs_terlaris = qs_terlaris.filter(sale_id__date_added__gte=start_of_week, sale_id__date_added__lt=end_of_week)
    else:
        qs_terlaris = qs_terlaris.filter(sale_id__date_added__gte=today_start, sale_id__date_added__lt=today_end)

    top_products = qs_terlaris.values('product_id__id', 'product_id__name', 'product_id__code', 'product_id__category_id__name') \
     .annotate(total_qty=Sum('qty')) \
     .order_by('-total_qty')[:5]

    context = {
        'page_title': 'Home',
        'categories': categories,
        'products': products,
        'transaction': transaction,
        'total_sales': int(chart_total_val),
        
        # Variabel Grafik Saham
        'chart_title': chart_title,
        'selected_period_name': selected_period_name,
        'chart_total_val': int(chart_total_val),
        'chart_growth_pct': chart_growth_pct,
        'is_chart_positive': is_chart_positive,
        'sales_dates': sales_dates,
        'sales_amounts': sales_amounts,
        
        'top_products': top_products,
    }
    return render(request, 'posApp/home.html', context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)


# ==========================================
# CATEGORIES
# ==========================================
@login_required
def category(request):
    category_list = Category.objects.all()
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)

@login_required
@user_passes_test(is_admin, login_url='/')
def manage_category(request):
    category = {}
    category_types = []
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
            if category:
                from posApp.models import CategoryType
                category_types = CategoryType.objects.filter(category=category)
    
    context = {
        'category' : category,
        'category_types': category_types
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
@user_passes_test(is_admin, login_url='/')
def save_category(request):
    data =  request.POST
    files = request.FILES
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            # MODE UPDATE
            cat = Category.objects.filter(id=data['id']).first()
            cat.name = data['name']
            
            # Remove legacy type strings from description if they exist
            desc = data['description']
            if '|||' in desc:
                desc = desc.split('|||')[0]
            cat.description = desc
            
            cat.status = data['status']
            if 'image' in files:
                cat.image = files['image']
            cat.save()
        else:
            # MODE TAMBAH BARU
            desc = data['description']
            if '|||' in desc:
                desc = desc.split('|||')[0]
                
            cat = Category(name=data['name'], description=desc, status=data['status'])
            if 'image' in files:
                cat.image = files['image']
            cat.save()
            
        # PROSES CATEGORY TYPES
        from posApp.models import CategoryType
        type_names = data.get('type_names_list', '').split('|||')
        type_names = [t.strip() for t in type_names if t.strip()]
        
        # Simpan atau update tipe
        existing_types = CategoryType.objects.filter(category=cat)
        existing_names = [t.name for t in existing_types]
        
        # Hapus tipe yang tidak ada di form
        for et in existing_types:
            if et.name not in type_names:
                et.delete()
                
        # Tambah atau update gambar
        for idx, t_name in enumerate(type_names):
            ctype, created = CategoryType.objects.get_or_create(category=cat, name=t_name)
            
            # File dikirim dengan key type_img_0, type_img_1, dst.
            file_key = f'type_img_{idx}'
            if file_key in files:
                ctype.image = files[file_key]
                ctype.save()
            
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
@user_passes_test(is_admin, login_url='/')
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


# ==========================================
# PRODUCTS
# ==========================================
@login_required
def products(request):
    product_list = Products.objects.all()
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)

@login_required
@user_passes_test(is_admin, login_url='/')
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1).prefetch_related('types')
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()
    
    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)

def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'posApp/test.html',context)

@login_required
@user_passes_test(is_admin, login_url='/')
def save_product(request):
    data = request.POST
    files = request.FILES 
    resp = {'status':'failed'}
    id = ''
    
    if 'id' in data:
        id = data['id']
        
    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=data['code']).all()
    else:
        check = Products.objects.filter(code=data['code']).all()
        
    if len(check) > 0 :
        resp['msg'] = "Kode SKU sudah digunakan oleh produk lain."
    else:
        category = Category.objects.filter(id = data['category_id']).first()
        try:
            # ==========================================
            # PENCEGAHAN NILAI KOSONG (ANTI-ERROR)
            # ==========================================
            stock_input = data.get('stock', 0)
            if stock_input == '': stock_input = 0
            
            warranty_input = data.get('warranty', 0)
            if warranty_input == '': warranty_input = 0
            
            buy_price_input = data.get('buy_price', 0)
            if buy_price_input == '': buy_price_input = 0
            # ==========================================

            if id.isnumeric() and int(id) > 0 :
                # MODE UPDATE
                prod = Products.objects.filter(id=id).first()
                prod.code = data['code']
                prod.category_id = category
                prod.name = data['name']
                prod.description = data['description']
                prod.price = float(data['price'])
                prod.buy_price = float(buy_price_input)
                prod.status = data['status']
                
                # Masukkan data aman
                prod.stock = int(stock_input)
                prod.warranty = int(warranty_input)
                
                if 'image' in files:
                    prod.image = files['image']
                prod.save()
            else:
                # MODE TAMBAH BARU
                prod = Products(
                    code=data['code'], 
                    category_id=category, 
                    name=data['name'], 
                    description=data['description'], 
                    price=float(data['price']),
                    buy_price=float(buy_price_input),
                    status=data['status'],
                    stock=int(stock_input),
                    warranty=int(warranty_input)
                )
                if 'image' in files:
                    prod.image = files['image']
                prod.save()
                
            resp['status'] = 'success'
        except Exception as e:
            resp['status'] = 'failed'
            resp['msg'] = str(e)
            
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
@user_passes_test(is_admin, login_url='/')
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


# ==========================================
# POS (KASIR & ADMIN BEBAS)
# ==========================================
@login_required
def pos(request):
    products = Products.objects.filter(status = 1)
    product_json = []
    for product in products:
        product_json.append({
            'id': product.id, 
            'name': product.name, 
            'price': float(product.price),
            'stock': product.stock
        })
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    return render(request, 'posApp/pos.html',context)

@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)

@login_required
def save_pos(request):
    resp = {'status':'failed','msg':''}
    data = request.POST
    pref = datetime.now().year  # Prefix = Tahun saat ini (misal: 2025)
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code = str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        # ==========================================
        # VALIDASI STOK
        # ==========================================
        idx = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod
            qty = data.getlist('qty[]')[idx]
            product = Products.objects.filter(id=product_id).first()
            if product:
                if product.stock - int(float(qty)) < 0:
                    resp['msg'] = f"Stok {product.name} tidak cukup."
                    return HttpResponse(json.dumps(resp), content_type="application/json")
            idx += 1

        payment = data.get('payment_method', 'Tunai')
        
        grand_total_val = float(data.get('grand_total', 0))
        tendered_amount_val = float(data.get('tendered_amount', 0))
        amount_change_val = float(data.get('amount_change', 0))

        if payment.lower() == 'qris':
            tendered_amount_val = grand_total_val
            amount_change_val = 0.0 

        # ==========================================
        # PENYIMPANAN DATA SALES (TERMASUK CUSTOMER)
        # ==========================================
        sales = Sales(
            code=code, 
            sub_total=data.get('sub_total', 0), 
            diskon=data.get('diskon', 0), 
            diskon_amount=data.get('diskon_amount', 0), 
            grand_total=grand_total_val, 
            tendered_amount=tendered_amount_val, 
            amount_change=amount_change_val,     
            payment_method=payment,
            # TANGKAP DATA PELANGGAN DARI FORM HTML
            customer_name=data.get('customer_name', ''),
            customer_wa=data.get('customer_wa', ''),
            customer_address=data.get('customer_address', ''),
            # KASIR YANG MEMPROSES
            cashier=request.user
        )
        sales.save()
        sale_id = sales.pk
        
        i = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod 
            sale = Sales.objects.filter(id=sale_id).first()
            product = Products.objects.filter(id=product_id).first()
            qty = data.getlist('qty[]')[i] 
            price = data.getlist('price[]')[i] 
            total = float(qty) * float(price)
            
            if product:
                stock_before = product.stock
                product.stock = product.stock - int(float(qty))
                product.save()

                InventoryLog(
                    product=product,
                    movement_type="KELUAR",
                    quantity_change=-int(float(qty)),
                    stock_before=stock_before,
                    stock_after=product.stock,
                    reference_code=code,
                    note="Terjual via POS",
                    recorded_by=request.user
                ).save()

            salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
            i += int(1)
            
        resp['status'] = 'success'
        resp['sale_id'] = sale_id
        
    except Exception as e:
        resp['msg'] = "An error occured: " + str(e)
        print("Unexpected error:", sys.exc_info()[0])
        
    return HttpResponse(json.dumps(resp),content_type="application/json")


# ==========================================
# SALES TRANSACTIONS
# ==========================================
@login_required
def salesList(request):
    # Mengambil data dari yang pertama sampai akhir
    sales = Sales.objects.all().order_by('id')
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        
        # Tambahan info Kasir
        if sale.cashier:
            data['cashier_name'] = sale.cashier.first_name if sale.cashier.first_name else sale.cashier.username
        else:
            data['cashier_name'] = 'Admin'

        data['items'] = salesItems.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'diskon_amount' in data:
            data['diskon_amount'] = format(float(data['diskon_amount']),'.2f')
        sale_data.append(data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    return render(request, 'posApp/sales.html',context)

@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
            
    if sales.cashier:
        transaction['cashier_name'] = sales.cashier.first_name if sales.cashier.first_name else sales.cashier.username
    else:
        transaction['cashier_name'] = 'Admin'

    if 'diskon_amount' in transaction:
        transaction['diskon_amount'] = format(float(transaction['diskon_amount']))
        
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList
    }
    return render(request, 'posApp/receipt.html',context)

@login_required
@user_passes_test(is_admin, login_url='/')
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        sale = Sales.objects.filter(id=id).first()
        code = sale.code if sale else ""
        
        sale_items = salesItems.objects.filter(sale_id=id)
        for item in sale_items:
            product = item.product_id
            if product:
                stock_before = product.stock or 0
                product.stock = stock_before + int(float(item.qty))
                product.save()
                
                InventoryLog(
                    product=product,
                    movement_type="MASUK",
                    quantity_change=int(float(item.qty)),
                    stock_before=stock_before,
                    stock_after=product.stock,
                    reference_code=code,
                    note=f"Pengembalian dari hapus transaksi {code}",
                    recorded_by=request.user
                ).save()

        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')


# ==========================================
# API PENGINTAI TRANSAKSI BARU (AJAX POLLING)
# ==========================================
@login_required
def check_new_sales(request):
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
        new_sales = Sales.objects.filter(id__gt=last_id).order_by('id')
        
        if new_sales.exists():
            latest_sale = new_sales.last()
            return JsonResponse({
                'status': 'new_data',
                'last_id': latest_sale.id,
                'code': latest_sale.code,
                'grand_total': latest_sale.grand_total
            })
            
        return JsonResponse({'status': 'no_data'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)})

# ==========================================
# INVENTORY MODULE
# ==========================================
@login_required
def inventory_list(request):
    logs = InventoryLog.objects.all().order_by('-date_added')
    
    # Filter
    product_id = request.GET.get('product')
    mov_type = request.GET.get('type')
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    
    if product_id:
        logs = logs.filter(product_id=product_id)
    if mov_type and mov_type != 'Semua':
        logs = logs.filter(movement_type=mov_type)
    if date_start:
        logs = logs.filter(date_added__date__gte=date_start)
    if date_end:
        logs = logs.filter(date_added__date__lte=date_end)
        
    total_masuk = sum(l.quantity_change for l in logs if l.movement_type == 'MASUK')
    total_keluar = sum(abs(l.quantity_change) for l in logs if l.movement_type == 'KELUAR')
    
    low_stock_count = Products.objects.filter(stock__lte=5, status=1).count()
    
    context = {
        'page_title': 'Log Inventory',
        'logs': logs,
        'products': Products.objects.filter(status=1),
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'low_stock_count': low_stock_count
    }
    return render(request, 'posApp/inventory.html', context)

@login_required
@user_passes_test(is_admin, login_url='/')
def inventory_add(request):
    if request.method == 'POST':
        resp = {'status':'failed', 'msg':''}
        try:
            product_id = request.POST.get('product_id')
            qty = int(request.POST.get('qty', 0))
            mov_type = request.POST.get('movement_type', 'Pembelian Baru')
            note = request.POST.get('note', '')
            buy_price = request.POST.get('buy_price', 0)
            if not buy_price: buy_price = 0
            
            product = Products.objects.filter(id=product_id).first()
            if product and qty > 0:
                stock_before = product.stock
                product.stock += qty
                product.save()
                
                InventoryLog(
                    product=product,
                    movement_type='MASUK',
                    quantity_change=qty,
                    stock_before=stock_before,
                    stock_after=product.stock,
                    note=f"[{mov_type}] {note}",
                    buy_price=float(buy_price),
                    recorded_by=request.user
                ).save()
                resp['status'] = 'success'
                messages.success(request, 'Stok masuk berhasil dicatat.')
            else:
                resp['msg'] = 'Produk tidak valid atau jumlah harus lebih dari 0.'
        except Exception as e:
            resp['msg'] = str(e)
        return HttpResponse(json.dumps(resp), content_type="application/json")
        
    context = {
        'products': Products.objects.filter(status=1)
    }
    return render(request, 'posApp/inventory_add.html', context)

@login_required
@user_passes_test(is_admin, login_url='/')
def inventory_adjust(request):
    if request.method == 'POST':
        resp = {'status':'failed', 'msg':''}
        try:
            product_id = request.POST.get('product_id')
            physical_stock = int(request.POST.get('physical_stock', 0))
            note = request.POST.get('note', '')
            
            product = Products.objects.filter(id=product_id).first()
            if product:
                stock_before = product.stock
                diff = physical_stock - stock_before
                
                if diff != 0:
                    product.stock = physical_stock
                    product.save()
                    
                    InventoryLog(
                        product=product,
                        movement_type='PENYESUAIAN',
                        quantity_change=diff,
                        stock_before=stock_before,
                        stock_after=product.stock,
                        note=note,
                        recorded_by=request.user
                    ).save()
                resp['status'] = 'success'
                messages.success(request, 'Penyesuaian stok berhasil disimpan.')
            else:
                resp['msg'] = 'Produk tidak ditemukan.'
        except Exception as e:
            resp['msg'] = str(e)
        return HttpResponse(json.dumps(resp), content_type="application/json")
        
    context = {
        'products': Products.objects.filter(status=1)
    }
    return render(request, 'posApp/inventory_adjust.html', context)

@login_required
def inventory_product(request, id):
    product = Products.objects.filter(id=id).first()
    logs = InventoryLog.objects.filter(product=product).order_by('-date_added')
    context = {
        'page_title': f'Detail Stok - {product.name}' if product else 'Detail Stok',
        'product': product,
        'logs': logs
    }
    return render(request, 'posApp/inventory_product.html', context)

@login_required
def inventory_low_stock(request):
    products = Products.objects.filter(stock__lte=5, status=1).order_by('stock')
    context = {
        'page_title': 'Produk Stok Menipis',
        'products': products
    }
    return render(request, 'posApp/inventory_low_stock.html', context)

@login_required
@user_passes_test(is_admin, login_url='/')
def inventory_edit_masuk(request):
    if request.method == 'POST':
        resp = {'status':'failed', 'msg':''}
        try:
            log_id = request.POST.get('id')
            new_qty = int(request.POST.get('new_qty', 0))
            note = request.POST.get('note', '')
            
            log = InventoryLog.objects.filter(id=log_id, movement_type='MASUK').first()
            if log and new_qty > 0:
                old_qty = log.quantity_change
                diff = new_qty - old_qty
                
                # Update current stock
                product = log.product
                product.stock += diff
                product.save()
                
                # Update log
                log.quantity_change = new_qty
                if note:
                    log.note = f"{log.note} | Edit: {note}"
                log.save()
                
                resp['status'] = 'success'
                messages.success(request, 'Data stok masuk berhasil diperbarui.')
            else:
                resp['msg'] = 'Log stok masuk tidak ditemukan atau jumlah tidak valid.'
        except Exception as e:
            resp['msg'] = str(e)
            print("Unexpected error:", sys.exc_info()[0])
        return HttpResponse(json.dumps(resp), content_type="application/json")
        
    log_id = request.GET.get('id')
    log = InventoryLog.objects.filter(id=log_id, movement_type='MASUK').first()
    context = {
        'log': log
    }
    return render(request, 'posApp/inventory_edit_masuk.html', context)

@login_required
@user_passes_test(is_admin, login_url='/')
def inventory_delete_masuk(request):
    resp = {'status':'failed', 'msg':''}
    try:
        log_id = request.POST.get('id')
        log = InventoryLog.objects.filter(id=log_id, movement_type='MASUK').first()
        
        if log:
            qty_to_revert = log.quantity_change
            product = log.product
            product.stock -= qty_to_revert
            product.save()
            
            log.delete()
            resp['status'] = 'success'
            messages.success(request, 'Riwayat stok masuk berhasil dihapus dan stok telah disesuaikan.')
        else:
            resp['msg'] = 'Data riwayat tidak ditemukan.'
    except Exception as e:
        resp['msg'] = str(e)
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
@user_passes_test(is_admin, login_url='/')
def inventory_report(request):
    products = Products.objects.filter(status=1).order_by('category_id__name', 'name')
    
    total_items = 0
    total_physical_stock = 0
    total_asset_value = 0
    total_potential_revenue = 0
    
    report_data = []
    
    for p in products:
        stock = p.stock or 0
        buy_price = p.buy_price or 0
        sell_price = p.price or 0
        
        asset_value = stock * buy_price
        potential_revenue = stock * sell_price
        
        total_items += 1
        total_physical_stock += stock
        total_asset_value += asset_value
        total_potential_revenue += potential_revenue
        
        report_data.append({
            'product': p,
            'asset_value': asset_value,
            'potential_revenue': potential_revenue
        })
        
    context = {
        'page_title': 'Laporan & Nilai Aset',
        'report_data': report_data,
        'total_items': total_items,
        'total_physical_stock': total_physical_stock,
        'total_asset_value': total_asset_value,
        'total_potential_revenue': total_potential_revenue
    }
    return render(request, 'posApp/inventory_report.html', context)