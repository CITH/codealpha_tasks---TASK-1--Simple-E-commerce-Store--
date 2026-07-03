import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Sum, Count
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Category, Product, Cart, CartItem, Coupon, Order, OrderItem, Wishlist, Review
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, ReviewForm

def get_or_create_cart(request):
    """Helper to retrieve the current cart, session-aware for anonymous users."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user__isnull=True)
                return cart
            except Cart.DoesNotExist:
                pass
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
        return cart

# ==============================================================================
# 1. CORE / CATALOG VIEWS
# ==============================================================================

def home_view(request):
    categories = Category.objects.all()[:5]
    featured_products = Product.objects.filter(is_featured=True)[:4]
    best_sellers = Product.objects.filter(is_best_seller=True)[:4]
    latest_reviews = Review.objects.all().order_by('-created_at')[:3]
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'latest_reviews': latest_reviews,
    }
    return render(request, 'shop/home.html', context)

def product_list_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # 1. Search Query
    q = request.GET.get('q', '')
    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(brand__icontains=q) | 
            Q(description__icontains=q)
        )
        
    # 2. Category Filter
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(category__slug=selected_category)
        
    # 3. Price Filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
            
    # 4. Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-id') # default newest
        
    # 5. Pagination
    paginator = Paginator(products, 6) # 6 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'q': q,
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'total_count': products.count(),
    }
    return render(request, 'shop/product_list.html', context)

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.all().order_by('-created_at')
    
    # Check if user already reviewed
    already_reviewed = False
    if request.user.is_authenticated:
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    
    review_form = ReviewForm()
    
    # Handle Rating / Review submission
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must log in to submit a review.")
            return redirect('login')
            
        if already_reviewed:
            messages.error(request, "You have already reviewed this product.")
            return redirect('product_detail', slug=product.slug)
            
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            # Recalculate average rating of product
            avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
            product.rating = round(avg_rating, 2)
            product.save()
            
            messages.success(request, "Thank you! Your review has been published.")
            return redirect('product_detail', slug=product.slug)
            
    # Simulate secondary product images
    gallery_images = [product.image.url if product.image else None]
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'already_reviewed': already_reviewed,
        'review_form': review_form,
        'gallery_images': gallery_images,
    }
    return render(request, 'shop/product_detail.html', context)

# ==============================================================================
# 2. AUTHENTICATION VIEWS
# ==============================================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to NovaCart, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
        
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username_or_email')
            password = form.cleaned_data.get('password')
            
            # Attempt to authenticate either with username or email
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is None:
                user = authenticate(username=username_or_email, password=password)
                
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = UserLoginForm()
        
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('home')

# ==============================================================================
# 3. SHOPPING CART (AJAX VIEWS)
# ==============================================================================

def cart_view(request):
    cart = get_or_create_cart(request)
    coupon_id = request.session.get('coupon_id')
    coupon = None
    discount = 0.00
    
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            if cart.total_price >= coupon.min_purchase:
                discount = float(coupon.discount_amount)
            else:
                # remove invalid coupon based on minimum amount
                del request.session['coupon_id']
                messages.warning(request, f"Coupon code {coupon.code} removed. Minimum purchase is ${coupon.min_purchase}.")
                coupon = None
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
            
    subtotal = float(cart.total_price)
    shipping = 10.00 if subtotal > 0 and subtotal < 150 else 0.00 # Free shipping over $150
    tax = round(subtotal * 0.05, 2) # 5% tax
    grand_total = max(0.00, subtotal + shipping + tax - discount)
    
    context = {
        'cart': cart,
        'coupon': coupon,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'shop/cart.html', context)

@require_POST
def cart_add_ajax(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        qty = int(data.get('quantity', 1))
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)
        
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        return JsonResponse({'success': False, 'error': 'Product is currently out of stock.'}, status=400)
        
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    new_qty = item.quantity + qty if not created else qty
    if new_qty > product.stock:
        return JsonResponse({'success': False, 'error': f'Only {product.stock} items available in stock.'}, status=400)
        
    item.quantity = new_qty
    item.save()
    
    return JsonResponse({
        'success': True,
        'message': f"Added {product.name} to cart.",
        'cart_count': cart.items_count
    })

@require_POST
def cart_update_ajax(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        qty = int(data.get('quantity'))
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)
        
    if qty <= 0:
        return JsonResponse({'success': False, 'error': 'Quantity must be at least 1.'}, status=400)
        
    item = get_object_or_404(CartItem, id=item_id)
    if qty > item.product.stock:
        return JsonResponse({'success': False, 'error': f'Only {item.product.stock} items left in stock.'}, status=400)
        
    item.quantity = qty
    item.save()
    
    cart = item.cart
    
    # Calculate cart-wide values
    coupon_id = request.session.get('coupon_id')
    discount = 0.00
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            if cart.total_price >= coupon.min_purchase:
                discount = float(coupon.discount_amount)
        except Coupon.DoesNotExist:
            pass
            
    subtotal = float(cart.total_price)
    shipping = 10.00 if subtotal > 0 and subtotal < 150 else 0.00
    tax = round(subtotal * 0.05, 2)
    grand_total = max(0.00, subtotal + shipping + tax - discount)
    
    return JsonResponse({
        'success': True,
        'message': 'Cart quantity updated.',
        'item_subtotal': float(item.subtotal),
        'cart_subtotal': subtotal,
        'cart_discount': discount,
        'cart_shipping': shipping,
        'cart_tax': tax,
        'cart_grand_total': grand_total,
        'cart_count': cart.items_count
    })

@require_POST
def cart_remove_ajax(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)
        
    item = get_object_or_404(CartItem, id=item_id)
    cart = item.cart
    item.delete()
    
    # Recalculate totals
    coupon_id = request.session.get('coupon_id')
    discount = 0.00
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            if cart.total_price >= coupon.min_purchase:
                discount = float(coupon.discount_amount)
            else:
                del request.session['coupon_id']
        except Coupon.DoesNotExist:
            pass
            
    subtotal = float(cart.total_price)
    shipping = 10.00 if subtotal > 0 and subtotal < 150 else 0.00
    tax = round(subtotal * 0.05, 2)
    grand_total = max(0.00, subtotal + shipping + tax - discount)
    
    return JsonResponse({
        'success': True,
        'message': 'Product removed from cart.',
        'cart_subtotal': subtotal,
        'cart_discount': discount,
        'cart_shipping': shipping,
        'cart_tax': tax,
        'cart_grand_total': grand_total,
        'cart_count': cart.items_count
    })

@require_POST
def apply_coupon_ajax(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid payload.'}, status=400)
        
    cart = get_or_create_cart(request)
    if cart.items_count == 0:
        return JsonResponse({'success': False, 'error': 'Your cart is empty.'}, status=400)
        
    try:
        coupon = Coupon.objects.get(code=code, active=True)
        subtotal = float(cart.total_price)
        
        if subtotal < float(coupon.min_purchase):
            return JsonResponse({
                'success': False, 
                'error': f'Coupon requires a minimum order of ${coupon.min_purchase}. your current is ${subtotal:.2f}.'
            }, status=400)
            
        request.session['coupon_id'] = coupon.id
        
        shipping = 10.00 if subtotal > 0 and subtotal < 150 else 0.00
        tax = round(subtotal * 0.05, 2)
        discount = float(coupon.discount_amount)
        grand_total = max(0.00, subtotal + shipping + tax - discount)
        
        return JsonResponse({
            'success': True,
            'message': f"Coupon '{code}' applied successfully!",
            'discount': discount,
            'cart_shipping': shipping,
            'cart_tax': tax,
            'cart_grand_total': grand_total
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid or expired coupon code.'}, status=400)

# ==============================================================================
# 4. CHECKOUT & ORDER SUCCESS
# ==============================================================================

def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.items_count == 0:
        messages.error(request, "Your shopping cart is empty.")
        return redirect('product_list')
        
    coupon_id = request.session.get('coupon_id')
    coupon = None
    discount = 0.00
    subtotal = float(cart.total_price)
    
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            if subtotal >= float(coupon.min_purchase):
                discount = float(coupon.discount_amount)
        except Coupon.DoesNotExist:
            pass
            
    shipping = 10.00 if subtotal > 0 and subtotal < 150 else 0.00
    tax = round(subtotal * 0.05, 2)
    grand_total = max(0.00, subtotal + shipping + tax - discount)
    
    if request.method == 'POST':
        # Ship Data
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        payment_method = request.POST.get('payment_method')
        
        if not all([full_name, phone, email, address, city, state, postal_code, payment_method]):
            messages.error(request, "Please fill in all the shipping and payment details.")
            return redirect('checkout')
            
        # Inventory verification check
        for item in cart.items.all():
            if item.quantity > item.product.stock:
                messages.error(request, f"Insufficient stock for {item.product.name}. Only {item.product.stock} items left.")
                return redirect('cart')
                
        # Generate Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            phone=phone,
            email=email,
            shipping_address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            payment_method=payment_method,
            total_price=cart.total_price,
            shipping_cost=shipping,
            tax=tax,
            discount=discount,
            status='Pending'
        )
        
        # Populate Order Items & Deduct Stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
            
        # Flush Cart
        cart.items.all().delete()
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
            
        # Save order ID to session for success screen path security
        request.session['last_order_id'] = order.id
        
        return redirect('order_success')
        
    context = {
        'cart': cart,
        'coupon': coupon,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'shop/checkout.html', context)

def order_success_view(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        messages.error(request, "Order details could not be found.")
        return redirect('home')
        
    order = get_object_or_404(Order, id=order_id)
    est_delivery = order.created_at + timezone.timedelta(days=5)
    
    context = {
        'order': order,
        'est_delivery': est_delivery.strftime('%A, %b %d, %Y'),
    }
    return render(request, 'shop/success.html', context)

# ==============================================================================
# 5. USER DASHBOARD (PROFILE, WISHLIST, ORDERS)
# ==============================================================================

@login_required
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    # Pre-populate details address logic based on their last order
    last_order = orders.first()
    saved_address = None
    if last_order:
        saved_address = {
            'address': last_order.shipping_address,
            'city': last_order.city,
            'state': last_order.state,
            'postal_code': last_order.postal_code,
            'phone': last_order.phone
        }
        
    profile_form = UserProfileForm(instance=request.user)
    
    context = {
        'orders': orders,
        'wishlist_items': wishlist_items,
        'saved_address': saved_address,
        'profile_form': profile_form,
    }
    return render(request, 'shop/dashboard.html', context)

@login_required
@require_POST
def edit_profile_view(request):
    form = UserProfileForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Your profile details have been successfully updated.")
    else:
        messages.error(request, "Could not update profile. Correct errors.")
    return redirect('dashboard')

@login_required
@require_POST
def wishlist_toggle_ajax(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid body.'}, status=400)
        
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        wishlist_item.delete()
        added = False
        message = f"Removed {product.name} from your wishlist."
    else:
        added = True
        message = f"Added {product.name} to your wishlist."
        
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    return JsonResponse({
        'success': True,
        'added': added,
        'message': message,
        'wishlist_count': wishlist_count
    })

# ==============================================================================
# 6. STAFF CUSTOM ADMIN DASHBOARD (ANALYTICS & MANAGEMENT)
# ==============================================================================

@user_passes_test(lambda u: u.is_staff, login_url='login')
def admin_dashboard_view(request):
    # Statistics
    total_sales = Order.objects.filter(status='Delivered').aggregate(Sum('total_price'))['total_price__sum'] or 0.00
    pending_revenue = Order.objects.exclude(status='Delivered').exclude(status='Cancelled').aggregate(Sum('total_price'))['total_price__sum'] or 0.00
    orders_count = Order.objects.count()
    users_count = User.objects.count()
    products_count = Product.objects.count()
    categories_count = Category.objects.count()
    
    # Inventories warnings limit < 10 items
    low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Catalog items lists
    products_list = Product.objects.select_related('category').all().order_by('-id')
    categories_list = Category.objects.all()
    users_list = User.objects.all().order_by('-date_joined')
    
    # Quick order status change form
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_order_status':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status modified to {new_status}")
            return redirect('admin_dashboard')
            
        elif action == 'add_product':
            # Create a product form fields
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            brand = request.POST.get('brand')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            description = request.POST.get('description')
            specifications = request.POST.get('specifications')
            is_featured = request.POST.get('is_featured') == 'on'
            is_best_seller = request.POST.get('is_best_seller') == 'on'
            
            image_file = request.FILES.get('image')
            
            p_cat = get_object_or_404(Category, id=category_id)
            Product.objects.create(
                name=name,
                category=p_cat,
                brand=brand,
                price=price,
                stock=stock,
                description=description,
                specifications=specifications,
                is_featured=is_featured,
                is_best_seller=is_best_seller,
                image=image_file
            )
            messages.success(request, f"Successfully created product '{name}'")
            return redirect('admin_dashboard')
            
        elif action == 'create_category':
            cat_name = request.POST.get('category_name')
            Category.objects.create(name=cat_name)
            messages.success(request, f"Successfully created category '{cat_name}'")
            return redirect('admin_dashboard')
            
    context = {
        'total_sales': total_sales,
        'pending_revenue': pending_revenue,
        'orders_count': orders_count,
        'users_count': users_count,
        'products_count': products_count,
        'categories_count': categories_count,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'products_list': products_list,
        'categories_list': categories_list,
        'users_list': users_list,
    }
    return render(request, 'shop/admin_dashboard.html', context)
