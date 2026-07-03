from django.urls import path
from . import views

urlpatterns = [
    # Core pages
    path('', views.home_view, name='home'),
    path('shop/', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Shopping Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add-ajax/', views.cart_add_ajax, name='cart_add_ajax'),
    path('cart/update-ajax/', views.cart_update_ajax, name='cart_update_ajax'),
    path('cart/remove-ajax/', views.cart_remove_ajax, name='cart_remove_ajax'),
    path('cart/apply-coupon-ajax/', views.apply_coupon_ajax, name='apply_coupon_ajax'),
    
    # Checkout workflow
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/', views.order_success_view, name='order_success'),
    
    # User Profile & Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('wishlist/toggle-ajax/', views.wishlist_toggle_ajax, name='wishlist_toggle_ajax'),
    
    # Staff Admin Custom Dashboard
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
