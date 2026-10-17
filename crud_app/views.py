from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User

from .decorators import admin_required
from .forms import CategoryForm, CheckoutForm, ProductForm
from .models import Category, Order, OrderItem, Product


def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:3]
    return render(request, 'product_detail.html', {'product': product, 'related': related})


@admin_required
def create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Produto "{product.name}" cadastrado com sucesso.')
            return redirect('home')
    else:
        form = ProductForm()
    context = {'form': form, 'has_categories': Category.objects.exists()}
    return render(request, 'create.html', context)


@admin_required
def update(request):
    return render(request, 'update.html', {'products': Product.objects.all()})


@admin_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Produto "{product.name}" atualizado com sucesso.')
            return redirect('update')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form, 'product': product})


@admin_required
def delete(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=request.POST.get('product_id'))
        name = product.name
        product.delete()
        messages.success(request, f'Produto "{name}" excluído com sucesso.')
        return redirect('delete')

    return render(request, 'delete.html', {'products': Product.objects.all()})


@admin_required
def categories(request):
    return render(request, 'categories.html', {'categories': Category.objects.all()})


@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria "{category.name}" cadastrada com sucesso.')
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, 'category_create.html', {'form': form})


@admin_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria "{category.name}" atualizada com sucesso.')
            return redirect('categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_update.html', {'form': form, 'category': category})


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Categoria "{name}" excluída com sucesso.')
        return redirect('categories')
    return redirect('categories')


def _cart_items(session_cart):
    items = []
    total = 0
    for product_id, qty in session_cart.items():
        product = Product.objects.filter(pk=product_id).first()
        if product is None:
            continue
        subtotal = product.price * qty
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
        total += subtotal
    return items, total


@login_required
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart
        messages.success(request, f'"{product.name}" adicionado ao carrinho.')
    return redirect(request.META.get('HTTP_REFERER') or 'home')


@login_required
def remove_from_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart.pop(str(pk), None)
        request.session['cart'] = cart
        messages.success(request, 'Produto removido do carrinho.')
    return redirect('cart')


@login_required
def cart(request):
    items, total = _cart_items(request.session.get('cart', {}))
    return render(request, 'cart.html', {'items': items, 'total': total})


@login_required
def checkout(request):
    items, total = _cart_items(request.session.get('cart', {}))

    if request.method == 'POST':
        if not items:
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('cart')
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                payment=form.cleaned_data['payment'],
                total=total,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    qty=item['qty'],
                    price=item['product'].price,
                )
            request.session['cart'] = {}
            messages.success(request, 'Compra finalizada com sucesso (demonstração).')
            return render(
                request,
                'checkout_success.html',
                {'customer_name': form.cleaned_data['name'], 'order': order},
            )
    else:
        if not items:
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('cart')
        form = CheckoutForm()

    return render(request, 'checkout.html', {'form': form, 'items': items, 'total': total})


@admin_required
def dashboard(request):
    today = timezone.localdate()
    first_of_month = today.replace(day=1)

    def sales(**filters):
        return Order.objects.filter(**filters).aggregate(
            count=Count('id'), total=Sum('total')
        )

    day = sales(created_at__date=today)
    month = sales(created_at__date__gte=first_of_month)

    top_raw = (
        OrderItem.objects.values('product__name', 'product__price')
        .annotate(qty=Sum('qty'))
        .order_by('-qty')[:5]
    )
    top_products = [
        {
            'product__name': row['product__name'],
            'qty': row['qty'],
            'revenue': row['qty'] * row['product__price'],
        }
        for row in top_raw
    ]

    week = []
    for offset in range(6, -1, -1):
        day_date = today - timedelta(days=offset)
        stats = sales(created_at__date=day_date)
        week.append({
            'date': day_date,
            'count': stats['count'] or 0,
            'total': stats['total'] or 0,
        })

    month_count = month['count'] or 0
    month_total = month['total'] or 0

    context = {
        'today': today,
        'sales_day_count': day['count'] or 0,
        'sales_day_total': day['total'] or 0,
        'sales_month_count': month_count,
        'sales_month_total': month_total,
        'avg_ticket': month_total // month_count if month_count else 0,
        'clients_count': User.objects.filter(user_type='client').count(),
        'products_count': Product.objects.count(),
        'top_products': top_products,
        'max_top_qty': max((p['qty'] for p in top_products), default=0),
        'week': week,
        'max_day_count': max((d['count'] for d in week), default=0),
        'recent_orders': Order.objects.select_related('user')[:5],
    }
    return render(request, 'dashboard.html', context)
