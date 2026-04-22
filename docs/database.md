# Database Schema

The system uses a relational schema designed for scalability and data integrity.

## 📊 Main Models

### Users & Profiles
- `User`: Custom user with `role` and `is_verified` flags.
- `UserProfile`: Extended details (phone, bio, image) linked 1:1 to User.
- `Address`: Multiple delivery addresses per user.

### Vendor & Catalog
- `Vendor`: Store details linked 1:1 to a User with a vendor role.
- `Category`: Self-referencing (parent-child) categories for deep nesting.
- `Product`: Main item details, stock, and price.
- `ProductImage`: Multiple images per product with ordering and "main" flag.

### Sales & Fulfillment
- `Cart` & `CartItem`: Temporary items for customers.
- `Order`: Global transaction tracking total amount and shipping.
- `OrderItem`: Individual products within an order, tracked by status (Pending, Shipped, etc.) for vendor fulfillment.

### Engagement
- `Review`: Ratings (1-5) and comments for products.
- `Wishlist`: Simple many-to-many relationship between Users and Products.
