import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from apps.users.models import User
from apps.vendor.models import Vendor
from apps.review.models import Review
from apps.products.models import (
    Category, Product, ProductAttribute, 
    ProductAttributeValue, ProductVariant, ProductSpecification, ProductImage
)

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with fake data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--vendors', type=int, default=5)
        parser.add_argument('--customers', type=int, default=10)
        parser.add_argument('--products', type=int, default=30)
        parser.add_argument('--reviews', type=int, default=5) # Max reviews per product

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # 1. Create Categories (Use get_or_create to avoid slug duplicates)
        categories = []
        category_names = ['Electronics', 'Fashion', 'Home & Garden', 'Beauty', 'Sports', 'Toys']
        for name in category_names:
            cat, created = Category.objects.get_or_create(
                name=name, 
                defaults={'description': fake.sentence()}
            )
            categories.append(cat)
            
            # Subcategories
            for i in range(2):
                sub_name = f"Sub {name} {i+1}"
                sub_cat, _ = Category.objects.get_or_create(
                    name=sub_name,
                    defaults={'parent': cat, 'description': fake.sentence()}
                )

        # 2. Create Attributes (Colors/Sizes)
        color_attr, _ = ProductAttribute.objects.get_or_create(name='Color')
        size_attr, _ = ProductAttribute.objects.get_or_create(name='Size')
        
        colors = ['Red', 'Blue', 'Black', 'White', 'Green']
        sizes = ['S', 'M', 'L', 'XL']
        
        color_values = [ProductAttributeValue.objects.get_or_create(attribute=color_attr, value=c)[0] for c in colors]
        size_values = [ProductAttributeValue.objects.get_or_create(attribute=size_attr, value=s)[0] for s in sizes]

        # 3. Create Vendors (Use random emails to avoid conflicts)
        vendors = []
        for i in range(options['vendors']):
            username = f"{fake.user_name()}_{random.randint(1000, 9999)}"
            email = f"vendor_{username}@example.com"
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                role='vendor',
                is_verified=True
            )
            vendor = Vendor.objects.create(
                user=user,
                store_name=fake.company(),
                store_description=fake.catch_phrase(),
                is_approved=True
            )
            vendors.append(vendor)

        # 4. Create Customers
        customers = []
        for i in range(options['customers']):
            username = f"{fake.user_name()}_{random.randint(1000, 9999)}"
            user = User.objects.create_user(
                username=username,
                email=f"customer_{username}@example.com",
                password='password123',
                role='customer',
                is_verified=True
            )
            customers.append(user)

        # 5. Create Products
        products = []
        for i in range(options['products']):
            price = random.randint(10, 500)
            on_sale = random.choice([True, False])
            discount_price = price * 0.8 if on_sale else None
            
            product = Product.objects.create(
                vendor=random.choice(vendors),
                category=random.choice(categories),
                name=fake.word().capitalize() + " " + fake.word(),
                description=fake.paragraph(nb_sentences=5),
                price=price,
                discount_price=discount_price,
                stock=random.randint(10, 100),
                status=random.choice(['published', 'published', 'published', 'pending']), # Weighted towards published
                is_featured=random.choice([True, False, False, False]),
                views_count=random.randint(0, 500)
            )
            products.append(product)

            # Add Variants
            for j in range(random.randint(2, 4)):
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=f"SKU-{product.id}-{j}",
                    price=product.price + random.randint(5, 10),
                    stock=random.randint(5, 20)
                )
                variant.attribute_values.add(random.choice(color_values))
                variant.attribute_values.add(random.choice(size_values))

            # Add Specifications
            for k in range(3):
                ProductSpecification.objects.create(
                    product=product,
                    key=fake.word().capitalize(),
                    value=fake.word()
                )

        # 6. Create Reviews
        for product in products:
            if product.status == 'published':
                num_reviews = random.randint(0, options['reviews'])
                reviewers = random.sample(customers, min(num_reviews, len(customers)))
                for reviewer in reviewers:
                    Review.objects.create(
                        product=product,
                        user=reviewer,
                        rating=random.randint(3, 5), # Customers usually leave 3-5 star reviews in fake data
                        comment=fake.sentence()
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {options['vendors']} vendors, {options['customers']} customers, {options['products']} products and reviews"))
