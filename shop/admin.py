from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Coupon, Order, OrderItem, Wishlist, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductAdminSpecificationsInline(admin.StackedInline):
    # A cleaner inline to read details: specs can also be edited as text
    pass

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'brand',
        'price',
        'stock',
        'rating',
        'is_featured',
        'is_best_seller'
    )

    list_filter = (
        'category',
        'brand',
        'is_featured',
        'is_best_seller'
    )

    search_fields = (
        'name',
        'brand',
        'description'
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    fields = (
        'name',
        'slug',
        'category',
        'brand',
        'description',
        'price',
        'stock',
        'rating',
        'image',
        'is_featured',
        'is_best_seller'
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'items_count')
    # inlines = [CartItemInline]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'min_purchase', 'active')
    list_filter = ('active',)
    search_fields = ('code',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'city', 'payment_method', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('id', 'full_name', 'email', 'phone', 'city')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]
    list_editable = ('status',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'created_at')
    list_filter = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment',)
