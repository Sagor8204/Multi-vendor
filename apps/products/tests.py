from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.vendor.models import Vendor
from apps.products.models import Category, Product

class ProductSearchTests(APITestCase):
    def setUp(self):
        # Create Category
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        
        # Create Vendor User
        self.vendor_user = User.objects.create_user(
            username="vendor", email="vendor@example.com", password="password123", role="vendor"
        )
        self.vendor = Vendor.objects.create(user=self.vendor_user, store_name="Tech Store")
        
        # Create Products
        self.product1 = Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name="Gaming Laptop",
            description="High performance gaming laptop",
            price=1200.00,
            status='published',
            is_active=True
        )
        self.product2 = Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name="Smartphone",
            description="Latest flagship smartphone",
            price=800.00,
            status='published',
            is_active=True
        )
        self.product3 = Product.objects.create(
            vendor=self.vendor,
            category=self.category,
            name="Office Chair",
            description="Ergonomic office chair",
            price=200.00,
            status='published',
            is_active=True
        )

    def test_search_by_query(self):
        url = reverse('products:product-search')
        response = self.client.get(url, {'q': 'laptop'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Gaming Laptop")

    def test_search_by_category(self):
        url = reverse('products:product-search')
        response = self.client.get(url, {'category': 'electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)

    def test_search_by_price_range(self):
        url = reverse('products:product-search')
        response = self.client.get(url, {'min_price': 500, 'max_price': 1000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Smartphone")

    def test_search_sorting_price_low(self):
        url = reverse('products:product-search')
        response = self.client.get(url, {'sort': 'price_low'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]['name'], "Office Chair")
        self.assertEqual(response.data['data'][2]['name'], "Gaming Laptop")
