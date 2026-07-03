from .models import Cart, Wishlist

def cart_and_wishlist(request):
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        # Get or create cart for logged in user
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items_count
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        # Merge anonymous cart if exists in session
        session_cart_id = request.session.get('cart_id')
        if session_cart_id:
            try:
                session_cart = Cart.objects.get(id=session_cart_id, user__isnull=True)
                for item in session_cart.items.all():
                    user_item, created = cart.items.get_or_create(
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not created:
                        user_item.quantity += item.quantity
                        user_item.save()
                session_cart.delete()
                del request.session['cart_id']
                cart_count = cart.items_count  # Recalculate
            except Cart.DoesNotExist:
                pass
    else:
        # Check anonymous cart
        session_cart_id = request.session.get('cart_id')
        if session_cart_id:
            try:
                cart = Cart.objects.get(id=session_cart_id, user__isnull=True)
                cart_count = cart.items_count
            except Cart.DoesNotExist:
                pass
                
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count
    }
