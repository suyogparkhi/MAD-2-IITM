# A-Z Household Services - Frontend

This is the frontend application for the A-Z Household Services platform, built with Vue.js.

## Project Overview

A-Z Household Services is a platform that connects customers with professional service providers for various household services. The application supports three user roles:

- **Customers**: Can request services, view service history, and leave reviews
- **Professionals**: Can view and accept service requests, manage their schedule, and view their ratings
- **Administrators**: Can manage users, services, and view reports

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Project Setup

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:

```
npm install
```

4. Create a `.env` file in the root directory with the following content:

```
VUE_APP_API_URL=http://localhost:5000/api
```

## Running the Application

### Development Server

```
npm run serve
```

This will start the development server at `http://localhost:8080`.

### Production Build

```
npm run build
```

This will create a production-ready build in the `dist` directory.

## Project Structure

- `src/`
  - `assets/` - Static assets like images and global CSS
  - `components/` - Reusable Vue components
    - `common/` - Shared components like Navbar, Footer, etc.
    - `admin/` - Admin-specific components
    - `customer/` - Customer-specific components
    - `professional/` - Professional-specific components
  - `views/` - Page components corresponding to routes
    - `auth/` - Authentication-related views (Login, Register, etc.)
    - `admin/` - Admin dashboard and related views
    - `customer/` - Customer dashboard and related views
    - `professional/` - Professional dashboard and related views
  - `router/` - Vue Router configuration
  - `store/` - Vuex store modules
    - `modules/` - Separate store modules for different features
  - `services/` - API service modules
  - `utils/` - Utility functions and helpers
  - `App.vue` - Root component
  - `main.js` - Application entry point

## Features

- User authentication (login, register, logout)
- Role-based access control
- Service request management
- User profile management
- Admin dashboard for system management
- Professional verification workflow
- Service reviews and ratings
- Responsive design

## API Integration

The frontend communicates with the backend API using Axios. The base URL for API requests is configured in the `.env` file and can be accessed throughout the application.

## Authentication

The application uses token-based authentication. Upon successful login, the token is stored in localStorage and included in the Authorization header for subsequent API requests.

## Development Guidelines

- Follow the Vue.js style guide
- Use Vuex for state management
- Use Vue Router for navigation
- Use Bootstrap for UI components and styling
- Write clean, maintainable, and well-documented code

## Deployment

The application can be deployed to any static hosting service after building with `npm run build`.

## License

[MIT License](LICENSE)
