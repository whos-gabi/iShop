"""
Fisier creat cu scopul de automatica popularea bazei de date
"""

import os
import django
import random
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iShopProject.settings")
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Product, Review, Order, OrderItem, Coupon

def run():
    # Creăm useri de test
    user1 = User.objects.create_user(username='john', email='john@example.com', password='password123')
    user2 = User.objects.create_user(username='jane', email='jane@example.com', password='password123')

    # Creăm categorii
    cat_phones = Category.objects.create(name='iPhones')
    cat_laptops = Category.objects.create(name='MacBooks')
    cat_accessories = Category.objects.create(name='Accessories')

    # Imagini disponibile
    images = ['products/image1.jpg', 'products/image2.jpg', 'products/image3.jpg']

    # Creăm produse
    product_names = [
        ('iPhone 13', cat_phones),
        ('iPhone 14 Pro', cat_phones),
        ('MacBook Air', cat_laptops),
        ('MacBook Pro', cat_laptops),
        ('Apple Watch', cat_accessories),
        ('AirPods', cat_accessories),
        ('iPad', cat_phones),
        ('Magic Keyboard', cat_accessories),
        ('iPhone SE', cat_phones),
        ('Mac Studio', cat_laptops),
    ]

    products = []
    for name, category in product_names:
        p = Product.objects.create(
            category=category,
            name=name,
            description=f"Descriere {name}",
            price=Decimal(random.randint(500, 3000)),
            stock=random.randint(10, 100),
        )
        products.append(p)

    # Creăm reviews (5 review-uri random)
    for i in range(5):
        product = random.choice(products)
        user = random.choice([user1, user2])
        rating = random.randint(1, 5)
        comment = f"Acesta este un review pentru {product.name}, rating: {rating}"
        Review.objects.create(
            product=product,
            user=user,
            rating=rating,
            comment=comment
        )

    # Creăm order-uri
    for i in range(3):
        order_user = random.choice([user1, user2])
        order = Order.objects.create(
            user=order_user,
            status='processing'
        )
        # Adăugăm 3 produse random în fiecare comandă
        selected_products = random.sample(products, 3)
        for prod in selected_products:
            quantity = random.randint(1, 5)
            OrderItem.objects.create(order=order, product=prod, quantity=quantity)

    # Creăm un coupon
    Coupon.objects.create(
        code='DISCOUNT10',
        discount_percentage=10,
        valid_from=timezone.now(),
        valid_to=timezone.now() + timezone.timedelta(days=30),
        active=True
    )

    print("Populare DB cu imagini terminată cu succes!")


if __name__ == '__main__':
    run()
