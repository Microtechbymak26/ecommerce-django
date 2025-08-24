from decimal import Decimal
from django.shortcuts import render,redirect,get_object_or_404
from .models import OrderItem, Product,Cart, Order , Category, Review
from customer.models import Address
from django.http import JsonResponse 
from django.db.models import Q , Sum 
from django.contrib import messages
from django.db.models import F
from django.contrib.auth.decorators import login_required

import json

# Create your views here.


@login_required
def add_review(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )
        messages.success(request, "✅ Your review has been submitted.")
        return redirect("product_detail", slug=product.slug)

def shop(request):
    products = Product.objects.all()
    selected_category = request.GET.get('category')
    categories = Category.objects.all()

    for product in products:
        if product.regular_price and product.regular_price > product.prize:
            product.discount_percent = int(((product.regular_price - product.prize) / product.regular_price) * 100)
        else:
            product.discount_percent = 0

    if selected_category:
        products = products.filter(category__id=selected_category)

    context = {
        "products": products,
        "categories": categories,
        "selected_category": int(selected_category) if selected_category else None
    }

    return render(request, "shop.html", context)   # ✅ fix

def home(request):
    categories = Category.objects.all()
    products = []

    # Har category ka sirf pehla product le lo
    for cat in categories:
        prod = Product.objects.filter(category=cat).order_by('id').first()
        if prod:
            products.append(prod)

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)




def product_detail(request, slug):
    product = Product.objects.get(status__iexact='Published',slug=slug)
    related_products = Product.objects.filter(category=product.category,status__iexact='Published').exclude(id=product.id)
    product_stock_range = range(1, product.stock + 1) if product.stock > 0 else []
    
    context = {
        'product': product,
        'related_products': related_products,
         'product_stock_range': product_stock_range
    }
    return render(request, 'product_detail.html', context=context)

from decimal import Decimal
from django.db.models import Q, Sum
from django.http import JsonResponse

# @login_required(login_url="userauths:sign-in")
def add_to_cart(request):


    if not request.user.is_authenticated:
         return JsonResponse({
                    'status': 'error',
                    'message': 'Please Sign in to add products to cart.'
                })  

    id = request.GET.get('id')
    qty = request.GET.get('qty')
    cart_id = request.GET.get('cart_id')
    variants_data = request.GET.get('variants')  # ✅ frontend se JSON string aayegi

    request.session['cart_id'] = cart_id

    if not id or not qty or not cart_id:
        return JsonResponse({'status': 'error', 'message': 'Missing required parameters.'})

    try:
        product = Product.objects.get(id=id, status__iexact='Published')
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found.'})

    existing_cart_items = Cart.objects.filter(cart_id=cart_id, product=product).first()

    if int(qty) > product.stock:
        return JsonResponse({'status': 'error', 'message': 'Insufficient stock available.'})

    if not existing_cart_items:
        cart = Cart()
        cart.product = product
        cart.quantity = qty
        cart.prize = product.prize
        cart.variants = variants_data  # ✅ yahan store hoga

        cart.cart_id = cart_id
        cart.sub_total = Decimal(product.prize) * Decimal(qty)
        cart.shipping = Decimal(product.shipping) + Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.save()

        message = 'Product added to cart successfully.'
    else:
        existing_cart_items.quantity = qty
        existing_cart_items.product = product
        existing_cart_items.prize = product.prize
        existing_cart_items.variants = variants_data  # ✅ update case me bhi save hoga

        existing_cart_items.cart_id = cart_id
        existing_cart_items.sub_total = Decimal(product.prize) * Decimal(qty)
        existing_cart_items.shipping = Decimal(product.shipping) + Decimal(qty)
        existing_cart_items.total = existing_cart_items.sub_total + existing_cart_items.shipping
        existing_cart_items.user = request.user if request.user.is_authenticated else None
        existing_cart_items.save()

        message = 'Product updated to cart successfully.'

    total_cart_items = Cart.objects.filter(cart_id=cart_id).count()
    cart_sub_total = Cart.objects.filter(cart_id=cart_id).aggregate(
        sub_total=Sum('sub_total')
    )['sub_total'] or 0.00

    return JsonResponse({
        'status': 'success',
        'message': message,
        'cart_id': cart_id,
        'total_cart_items': total_cart_items,
        'cart_sub_total': "{:,.2f}".format(cart_sub_total),
        'item_sub_total': "{:,.2f}".format(
            existing_cart_items.sub_total if existing_cart_items else cart.sub_total
        )
    })


def cart(request):
    cart_id = request.session.get("cart_id", None)

    items = Cart.objects.filter(
        Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)
    )

    # subtotal
    cart_sub_total = items.aggregate(sub_total=Sum('sub_total'))['sub_total'] or Decimal("0.00")
    # shipping total
    cart_shipping_total = items.aggregate(shipping=Sum('shipping'))['shipping'] or Decimal("0.00")
    # grand total
    cart_total = cart_sub_total + cart_shipping_total

    try:
        addresses = Address.objects.filter(user=request.user)
    except:
        addresses = None

    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    context = {
        'items': items,
        'cart_sub_total': cart_sub_total,
        'cart_shipping_total': cart_shipping_total,
        'cart_total': cart_total,
        'addresses': addresses,
    }

    return render(request, 'cart.html', context)


@login_required
def delete_cart_item(request):
    item_id = request.GET.get('item_id')
    product_id = request.GET.get('id')

    if not item_id or not product_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

    # ✅ check product
    try:
        product = Product.objects.get(id=product_id, status__iexact='Published')
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found.'})

    # ✅ delete only if item belongs to logged-in user
    try:
        item = Cart.objects.get(id=item_id, user=request.user)
        item.delete()
    except Cart.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cart item not found or not yours.'})

    # ✅ update totals for that user only
    total_cart_items = Cart.objects.filter(user=request.user)
    cart_sub_total = total_cart_items.aggregate(sub_total=Sum('sub_total'))['sub_total']

    return JsonResponse({
        'status': 'success',
        'message': 'Item deleted successfully.',
        'total_cart_items': total_cart_items.count(),
        'cart_sub_total': "{:,.2f}".format(cart_sub_total) if cart_sub_total else "0.00",
    })


def create_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')

        if not address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect('cart')
        
        address = Address.objects.get(id=address_id, user=request.user) 

        if 'cart_id' in request.session:
            cart_id = request.session['cart_id']
        else:
            cart_id = None
        items = Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id))
        cart_sub_total = Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)) \
            .aggregate(sub_total=Sum('sub_total'))['sub_total']
        cart_shipping_total = Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)) \
            .aggregate(shipping=Sum('shipping'))['shipping']
        
        order = Order()
        order.sub_total = cart_sub_total
        order.customer = request.user
        order.address = address
        order.shipping = cart_shipping_total
        order.total = order.sub_total + order.shipping
        order.save()


     
        for item in items:
            # CHANGE: yahan bhi variants ko store kar rahe hain
            # ✅ variants ko bhi yahan store karenge
            OrderItem.objects.create(
                order=order,
                product=item.product,
                qty=item.quantity,
                prize=item.prize,
                variants=item.variants,  # ✅ variants bhi yahan store karenge
                sub_total=item.sub_total,
                shipping=item.shipping,
                total=item.total,
                vendor=item.product.vendor  # Assuming product has a vendor field
            ) 
            order.vendors.add(item.product.vendor)  # Assuming product has a vendor field

        return redirect('checkout', order_id=order.id)


def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order
    }
    return render(request, 'checkout.html', context)


