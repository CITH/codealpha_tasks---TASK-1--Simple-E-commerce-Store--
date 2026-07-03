import os
import django

# Set up Django environment
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novacart.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Product, Coupon

def seed():
    print("Starting data seeding...")
    
    # 1. Create Superuser if doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@novacart.com', 'admin123')
        print("Admin user created: admin / admin123")
    else:
        print("Admin user already exists")

    # 2. Create Categories
    categories_data = [
        'Electronics',
        'Fashion',
        'Footwear',
        'Accessories',
        'Home Appliances'
    ]
    
    categories = {}
    for cat_name in categories_data:
        cat, created = Category.objects.get_or_create(name=cat_name)
        categories[cat_name] = cat
        if created:
            print(f"Created category: {cat_name}")

    # 3. Create Coupons
    coupons_data = [
        {'code': 'NOVA10', 'discount_amount': 10.00, 'min_purchase': 50.00},
        {'code': 'SAVE50', 'discount_amount': 50.00, 'min_purchase': 200.00},
        {'code': 'FREESHIP', 'discount_amount': 5.00, 'min_purchase': 20.00},
    ]
    for c_data in coupons_data:
        coupon, created = Coupon.objects.get_or_create(
            code=c_data['code'],
            defaults={
                'discount_amount': c_data['discount_amount'],
                'min_purchase': c_data['min_purchase'],
                'active': True
            }
        )
        if created:
            print(f"Created coupon: {coupon.code}")

    # 4. Create Products
    products_data = [
        {
            'name': 'Apple MacBook Air M3',
            'category': categories['Electronics'],
            'brand': 'Apple',
            'description': 'Supercharged by the next-generation M3 chip, the incredibly thin and fast MacBook Air features up to 18 hours of battery life and a stunning Liquid Retina display in an ultra-portable design.',
            'specifications': 'Chip: Apple M3 8-core CPU; RAM: 8GB unified memory; Storage: 256GB Superfast SSD; Display: 13.6-inch Liquid Retina; Keyboard: Backlit Magic Keyboard with Touch ID',
            'price': 1099.00,
            'stock': 12,
            'rating': 4.80,
            'is_featured': True,
            'is_best_seller': True,
        },
        {
            'name': 'Samsung Galaxy S25 Ultra',
            'category': categories['Electronics'],
            'brand': 'Samsung',
            'description': 'Meet the Galaxy S25 Ultra, the ultimate form of Galaxy Ultra. Powered by the latest Snapdragon 8 Gen 4 processor, featuring a massive 200MP camera system, and built-in S Pen for professional productivity.',
            'specifications': 'CPU: Snapdragon 8 Gen 4; RAM: 12GB; Storage: 256GB; Battery: 5000mAh with 45W Charging; Screen: 6.8-inch Dynamic AMOLED 2X 120Hz; OS: Android 15 with One UI 7',
            'price': 1299.99,
            'stock': 8,
            'rating': 4.90,
            'is_featured': True,
            'is_best_seller': False,
        },
        {
            'name': 'Sony WH-1000XM6',
            'category': categories['Electronics'],
            'brand': 'Sony',
            'description': 'Industry-leading noise canceling overhead headphones with premium sound, smart listening controls, and crystal-clear hands-free calling with advanced multipoint connections.',
            'specifications': 'Type: Over-Ear; ANC: Dual Noise Sensor Technology; Battery Life: Up to 40 hours; Rapid Charging: 5 min charge for 5 hours; Connectivity: Bluetooth 5.4 and Multipoint',
            'price': 398.00,
            'stock': 25,
            'rating': 4.70,
            'is_featured': True,
            'is_best_seller': True,
        },
        {
            'name': 'Apple Watch Series 10',
            'category': categories['Accessories'],
            'brand': 'Apple',
            'description': 'The most refined Apple Watch yet, featuring a thinner design, larger display with wide-angle OLED, sleep apnea notifications, faster charging, and advanced fitness tracking.',
            'specifications': 'Case size: 45mm; Material: Aluminum; Display: Always-On Retina; Water resistance: IP6X & 50m Swimproof; Battery: Fast charging up to 18 hours',
            'price': 399.00,
            'stock': 15,
            'rating': 4.60,
            'is_featured': False,
            'is_best_seller': True,
        },
        {
            'name': 'Logitech MX Master 3S',
            'category': categories['Accessories'],
            'brand': 'Logitech',
            'description': 'An iconic ergonomic mouse remastered. Feel every moment of your workflow with even more precision, tactile feedback, and quiet clicks, ideal for programmers and creative professionals.',
            'specifications': 'Sensor: 8,000 DPI Darkfield tracking; Buttons: 7 customisable keys; Scroll wheel: MagSpeed Electromagnetic; Connection: Bluetooth or Logi Bolt receiver',
            'price': 99.99,
            'stock': 30,
            'rating': 4.80,
            'is_featured': False,
            'is_best_seller': False,
        },
        {
            'name': 'Nike Air Max Running Shoes',
            'category': categories['Footwear'],
            'brand': 'Nike',
            'description': 'Take your runs further with legendary Air Max cushioning. Features breathable engineered mesh upper, plush padded collar, and durable rubber traction outsole.',
            'specifications': 'Type: Road Running; Cushioning: Max Air unit in heel; Upper: Breathable mesh; Closure: Lace-up',
            'price': 149.00,
            'stock': 40,
            'rating': 4.50,
            'is_featured': True,
            'is_best_seller': True,
        },
        {
            'name': 'Puma Flyride Running Shoes',
            'category': categories['Footwear'],
            'brand': 'Puma',
            'description': 'Engineered with Puma Nitro foam technology, the Flyride delivers maximum performance, energy return, and lightweight responsiveness for runners of all levels.',
            'specifications': 'Midsole: Nitro Foam; Weight: 245g; Outsole: Pumagrip high-traction rubber; Material: Engineered Knit',
            'price': 89.50,
            'stock': 35,
            'rating': 4.40,
            'is_featured': False,
            'is_best_seller': False,
        },
        {
            'name': 'boAt Airdopes 131',
            'category': categories['Accessories'],
            'brand': 'boAt',
            'description': 'Experience true wireless music with boAt Airdopes. Features custom 13mm audio drivers, instant IWP connection technology, and ergonomic earbud design.',
            'specifications': 'Driver Size: 13mm; Playtime: Up to 15 hours with case; Charging Port: Type-C; Voice Assistant: One-click support',
            'price': 29.99,
            'stock': 150,
            'rating': 4.10,
            'is_featured': False,
            'is_best_seller': True,
        },
        {
            'name': 'JBL Flip 6 Waterproof Speaker',
            'category': categories['Electronics'],
            'brand': 'JBL',
            'description': 'The JBL Flip 6 portable Bluetooth speaker delivers powerful JBL Original Pro Sound with exceptional clarity thanks to its 2-way speaker system. Waterproof and dustproof for outdoor adventures.',
            'specifications': 'Output: 30W RMS; Waterproofing: IP67; Battery Life: Up to 12 hours; Connection: Bluetooth 5.1 & PartyBoost',
            'price': 129.95,
            'stock': 50,
            'rating': 4.70,
            'is_featured': True,
            'is_best_seller': False,
        },
        {
            'name': 'Dell XPS 13 Laptop',
            'category': categories['Electronics'],
            'brand': 'Dell',
            'description': 'Crafted with premium materials like machined aluminum and carbon fiber, this masterclass laptop packs high-end Intel Core Ultra processor power in a stunningly compact bezel-less layout.',
            'specifications': 'CPU: Intel Core Ultra 7 155H; RAM: 16GB LPDDS5x; Storage: 512GB PCIe NVMe SSD; Display: 13.4-inch FHD+ anti-glare screen; Graphics: Intel Arc Graphics',
            'price': 1449.00,
            'stock': 6,
            'rating': 4.60,
            'is_featured': True,
            'is_best_seller': True,
        },
    ]

    for p_data in products_data:
        product, created = Product.objects.get_or_create(
            name=p_data['name'],
            defaults={
                'category': p_data['category'],
                'brand': p_data['brand'],
                'description': p_data['description'],
                'specifications': p_data['specifications'],
                'price': p_data['price'],
                'stock': p_data['stock'],
                'rating': p_data['rating'],
                'is_featured': p_data['is_featured'],
                'is_best_seller': p_data['is_best_seller']
            }
        )
        if created:
            print(f"Created product: {product.name}")

    print("Data seeding completed successfully!")

if __name__ == '__main__':
    seed()
