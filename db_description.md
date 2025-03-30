# Household Services Database Description

This database is designed for a household services application that connects customers with service professionals. The system allows customers to request services, professionals to provide those services, and administrators to manage the entire platform.

## Database Schema Overview

### Users
The `users` table is the central table that stores all user accounts regardless of their role (admin, customer, or professional). It contains basic authentication and identification information including username, email, and password hash. Each user has a specific role that determines their permissions and related profile information.

### Services
The `services` table contains the list of services that can be requested by customers and provided by professionals. Each service has a name, description, base price, and estimated time required for completion.

### Professionals
The `professionals` table extends the users table for users with the 'professional' role. Each professional is associated with one service they can provide, and includes additional information such as their experience level, verification status, uploaded document information, and contact details.

### Customers
The `customers` table extends the users table for users with the 'customer' role. It contains additional customer-specific information like address and pin code.

### Service Requests
The `service_requests` table is the core of the business logic, representing service requests created by customers. Each request is associated with a specific service and customer, and may be assigned to a professional. The request progresses through various statuses from 'requested' to 'completed' and finally 'closed'.

### Reviews
The `reviews` table stores customer feedback for completed service requests. Each review includes a rating (1-5 stars) and optional comments about the service provided.

### Export Jobs
The `export_jobs` table supports the administrative reporting functionality, tracking the status of data export operations requested by users (primarily admins). This enables asynchronous report generation for large datasets.

## Relationships

1. A user can have one professional profile or one customer profile (one-to-one relationship)
2. A service can be offered by many professionals (one-to-many relationship)
3. A professional can handle many service requests (one-to-many relationship)
4. A customer can create many service requests (one-to-many relationship)
5. A service request belongs to one customer, one service, and optionally one professional (many-to-one relationships)
6. A service request can have one review (one-to-one relationship)
7. A user can create many export jobs (one-to-many relationship)

This database design supports the core functionality of the household services platform while maintaining data integrity through appropriate relationships and constraints. 