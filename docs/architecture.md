# Architecture Overview

The Multi-Vendor Marketplace follows a modular Django architecture, separating concerns into specialized applications.

## 🏗 Modular Design

### 1. Core Layer (`apps/core`)
- Provides `BaseModel` (abstract) with standard `created_at`, `updated_at`, and `is_active` fields.
- Implements a standardized `api_response` utility for consistent JSON structure.
- Handles global file management.

### 2. Identity & Access (`apps/users`)
- Custom `User` model using `email` as the primary identifier.
- Role-based access control (Admin, Vendor, Customer).
- Signal-driven `UserProfile` creation on registration.

### 3. Vendor Ecosystem (`apps/vendor` & `apps/products`)
- Vendors manage their own stores and catalogs.
- Strict ownership validation ensures vendors can only modify their own products/images.

### 4. Transactional Flow (`apps/cart` & `apps/orders`)
- **Cart**: Temporary storage with real-time stock availability checks.
- **Orders**: Atomic conversion from cart to order, decrementing stock and creating fulfillment items for respective vendors.

## 🔒 Security
- **Authentication**: JWT (JSON Web Token) via SimpleJWT.
- **Authorization**: Custom permission classes to restrict access based on roles (e.g., `IsVendor`, `IsAdminUser`).
- **Data Integrity**: Database-level constraints and atomic transactions for order processing.
