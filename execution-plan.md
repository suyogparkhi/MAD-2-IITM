# Household Services Application V2 - Execution Plan

## 1. Project Overview

The Household Services Application V2 is a multi-user platform that connects customers with service professionals for various household services. The application serves three main user roles: Admin, Service Professional, and Customer, each with specific functionalities and access levels.

### Key Features:
- Role-based authentication and authorization
- Service management and service request handling
- Professional verification and management
- Customer service booking and review system
- Scheduled and user-triggered background jobs
- Performance optimization through caching

## 2. Technology Stack

### Backend:
- **Flask**: Web framework for building the API
- **SQLite**: Database for storing application data
- **Redis**: For caching and as a message broker
- **Celery**: For handling background jobs
- **JWT**: For authentication and authorization

### Frontend:
- **VueJS**: JavaScript framework for building the UI
- **Bootstrap**: CSS framework for styling
- **Axios**: For API calls from the frontend

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   VueJS     │     │   Flask     │     │  SQLite DB  │
│  Frontend   │────▶│   Backend   │────▶│             │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          │
                    ┌─────┴─────┐
                    │           │
              ┌─────▼─────┐    ┌▼────────┐
              │   Redis   │    │ Celery  │
              │           │    │         │
              └───────────┘    └─────────┘
```

### 3.2 Detailed Architecture

#### Frontend (VueJS + Bootstrap):
- **Public Module**: Landing page, login, registration
- **Admin Module**: Dashboard, service management, user management
- **Customer Module**: Service browsing, booking, reviews
- **Professional Module**: Request management, service completion

#### Backend (Flask):
- **API Layer**: RESTful endpoints for all functionalities
- **Authentication Layer**: JWT-based authentication
- **Service Layer**: Business logic
- **Data Access Layer**: Database operations

#### Background Processing (Redis + Celery):
- **Scheduled Jobs**: Daily reminders, monthly reports
- **User-Triggered Jobs**: CSV exports

#### Database (SQLite):
- Relational database with tables for users, services, requests, etc.

#### Caching (Redis):
- Cache frequently accessed data to improve performance

## 4. Database Design

### 4.1 Entity-Relationship Diagram

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│   User    │     │  Service  │     │  Request  │
├───────────┤     ├───────────┤     ├───────────┤
│ id        │     │ id        │     │ id        │
│ username  │     │ name      │     │ service_id│
│ password  │     │ price     │     │ customer_id│
│ email     │     │ time_req  │     │ pro_id    │
│ role      │     │ desc      │     │ req_date  │
│ status    │     │           │     │ comp_date │
└───────────┘     └───────────┘     │ status    │
     │                 │            │ remarks   │
     │                 │            └───────────┘
     │                 │                  │
┌────▼────┐     ┌─────▼───┐              │
│ Customer│     │Professional│◄───────────┘
├─────────┤     ├──────────┤
│ user_id │     │ user_id  │
│ address │     │ service_id│
│ pincode │     │ experience│
└─────────┘     │ verified │
                └──────────┘
                      │
                      ▼
                ┌──────────┐
                │  Review  │
                ├──────────┤
                │ id       │
                │ req_id   │
                │ rating   │
                │ comment  │
                │ date     │
                └──────────┘
```

### 4.2 Database Tables

1. **Users**
   - id (PK)
   - username
   - password (hashed)
   - email
   - role (admin/customer/professional)
   - status (active/blocked)
   - created_at

2. **Customers**
   - id (PK)
   - user_id (FK)
   - address
   - pincode
   - phone

3. **Professionals**
   - id (PK)
   - user_id (FK)
   - service_id (FK)
   - experience
   - description
   - verification_status
   - documents_url

4. **Services**
   - id (PK)
   - name
   - price
   - time_required
   - description

5. **ServiceRequests**
   - id (PK)
   - service_id (FK)
   - customer_id (FK)
   - professional_id (FK, nullable)
   - request_date
   - completion_date (nullable)
   - status (requested/assigned/rejected/completed/closed)
   - remarks

6. **Reviews**
   - id (PK)
   - request_id (FK)
   - rating
   - comment
   - date_posted

## 5. API Endpoints

### 5.1 Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### 5.2 Admin Endpoints

- `GET /api/admin/dashboard` - Admin dashboard data
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{id}/status` - Block/unblock user
- `GET /api/admin/professionals` - List all professionals
- `PUT /api/admin/professionals/{id}/verify` - Verify professional
- `POST /api/admin/services` - Create service
- `PUT /api/admin/services/{id}` - Update service
- `DELETE /api/admin/services/{id}` - Delete service
- `POST /api/admin/export/requests` - Trigger CSV export job

### 5.3 Customer Endpoints

- `GET /api/services` - List all services
- `GET /api/services/search` - Search services
- `POST /api/requests` - Create service request
- `PUT /api/requests/{id}` - Update service request
- `PUT /api/requests/{id}/close` - Close service request
- `POST /api/reviews` - Post review

### 5.4 Professional Endpoints

- `GET /api/professional/requests` - List assigned requests
- `PUT /api/professional/requests/{id}/accept` - Accept request
- `PUT /api/professional/requests/{id}/reject` - Reject request
- `PUT /api/professional/requests/{id}/complete` - Complete service

## 6. Background Jobs

### 6.1 Scheduled Jobs

1. **Daily Reminders**
   - Check for pending service requests
   - Send reminders to professionals via email/chat
   - Schedule: Daily at 6:00 PM

2. **Monthly Activity Reports**
   - Generate monthly service activity reports for customers
   - Send reports via email
   - Schedule: 1st day of every month at 8:00 AM

### 6.2 User-Triggered Jobs

1. **Export Service Requests as CSV**
   - Admin triggers export
   - Generate CSV with service request details
   - Notify admin when export is complete

## 7. Caching Strategy

- Cache service listings for faster retrieval
- Cache professional profiles based on ratings
- Cache authentication tokens
- Set appropriate expiry times for different cache types

## 8. Implementation Plan

### Phase 1: Setup and Basic Functionality (Week 1)
- Set up project structure
- Implement database models
- Set up authentication system
- Create basic API endpoints

### Phase 2: Core Features (Week 2)
- Implement service management
- Implement service request handling
- Develop professional verification flow
- Create customer booking system

### Phase 3: UI Development (Week 3)
- Develop admin dashboard
- Develop customer interface
- Develop professional interface
- Implement responsive design

### Phase 4: Background Jobs & Optimization (Week 4)
- Set up Celery and Redis
- Implement scheduled jobs
- Implement user-triggered jobs
- Optimize performance with caching

### Phase 5: Testing and Refinement (Week 5)
- Conduct unit and integration testing
- Fix bugs and issues
- Refine UI/UX
- Prepare documentation

## 9. Testing Strategy

### 9.1 Unit Testing
- Test individual components and functions
- Use pytest for backend testing
- Use Jest for frontend testing

### 9.2 Integration Testing
- Test API endpoints
- Test database operations
- Test background jobs

### 9.3 User Acceptance Testing
- Test admin workflows
- Test customer workflows
- Test professional workflows

## 10. Deliverables

1. Source code repository
2. Project documentation
3. API documentation
4. User guide
5. Testing reports
6. Presentation video

## 11. Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| Complex authentication | Use established libraries, follow best practices |
| Background job failures | Implement robust error handling and retry mechanisms |
| Performance issues | Utilize caching effectively, optimize database queries |
| UI/UX challenges | Follow Bootstrap guidelines, conduct usability testing |
| Integration issues | Use proper API design, thorough testing |
