# Multi-Vendor Marketplace API

A robust, scalable multi-vendor e-commerce platform built with Django Rest Framework (DRF) and PostgreSQL.

## 🚀 Key Features

- **Custom User Management**: JWT authentication with roles (Admin, Vendor, Customer) and automated profile creation.
- **Vendor System**: Store management, approval workflow, and vendor-specific dashboards.
- **Product Catalog**: Multi-category support, multi-image uploads, and stock management.
- **Shopping Cart**: Real-time stock validation and persistent cart storage.
- **Order Management**: Comprehensive order lifecycle (Pending, Paid, Shipped, Delivered, Cancelled) with vendor-specific fulfillment.
- **Customer Engagement**: Product reviews, ratings, and wishlist management.
- **Address Book**: Multi-address support with default selection.

## 🛠 Tech Stack

- **Backend**: Django & Django Rest Framework (DRF)
- **Authentication**: SimpleJWT
- **Documentation**: DRF-Spectacular (Swagger/ReDoc)
- **Database**: PostgreSQL (recommended for production)

## 📁 Project Structure

```text
├── apps/
│   ├── cart/        # Shopping cart and items
│   ├── core/        # Base models, utilities, and global files
│   ├── orders/      # Order processing and fulfillment
│   ├── payments/    # Payment gateway integrations (WIP)
│   ├── products/    # Catalog, categories, and images
│   ├── review/      # Ratings, reviews, and wishlists
│   ├── users/       # Custom user, profiles, and addresses
│   └── vendor/      # Store management and applications
├── config/          # Project settings and root URLs
└── docs/            # Technical documentation
```

## 🚥 Quick Start

1. **Clone the repository**
2. **Setup Environment**: Copy `.env.example` to `.env` and update credentials.
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Run Migrations**: `python manage.py migrate`
5. **Start Server**: `python manage.py runserver`

## 🧪 Seeding the Database

Populate your database with fake data for testing purposes using the custom management command:

```powershell
# Default: 5 vendors, 10 customers, 30 products
python manage.py seed_db

# Custom amounts:
python manage.py seed_db --vendors 10 --customers 50 --products 100 --reviews 10
```

## 📖 API Documentation

Once the server is running, access the interactive docs at:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc/`
