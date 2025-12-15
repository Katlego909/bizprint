# bizprint Project Overview

This is a Django web application named "bizprint", designed as an e-commerce and custom design service platform, likely catering to printing businesses. It allows users to browse products, request custom design services, manage their orders and design requests, and track their activities.

## Main Technologies

*   **Backend Framework:** Django (Python)
*   **API:** Django REST Framework (used for potential API endpoints)
*   **Database:** SQLite (for development, configurable for production)
*   **Static Files:** Whitenoise (for serving static assets efficiently)
*   **Image Processing:** Pillow
*   **Frontend:** Standard Django templates (HTML, CSS, JavaScript)
*   **External Integrations:**
    *   Twilio (for SMS/WhatsApp notifications, based on settings)
    *   Email (for order confirmations, newsletter discounts, contact forms)

## Project Structure and Core Functionalities

The project is organized into several Django applications:

*   **`products`:**
    *   Manages product catalog, categories, and their images.
    *   Implements complex product pricing with `QuantityTier`s, `ProductOption`s (configurable dropdowns), and `OptionalService` add-ons.
    *   Handles the entire order workflow: product selection, quantity, options, services, shipping, discount codes, payment proof uploads, and artwork uploads.
    *   Features include `Order` tracking, `invoice` generation, `my orders` listing, order cancellation, and contact support.
*   **`designs`:**
    *   Defines `DesignPackage` services.
    *   Manages `DesignRequest`s, allowing both logged-in users and guests to submit requests for custom designs, including file uploads and additional instructions.
    *   Generates unique `quote_token`s for guest access to design quotes.
    *   Includes functionality for displaying quotes, managing `my design requests`, and uploading proof of payment for design services.
*   **`accounts`:**
    *   Manages user registration, login, logout, and profile management.
    *   Extends Django's default `User` model with `CustomerProfile` for additional user details (phone, address).
    *   Features a user dashboard displaying recent orders and design requests.
    *   Includes a `NewsletterSubscriber` model for email subscriptions with automatic discount code generation.
*   **`bizprint` (project core):**
    *   Contains the main Django settings (`settings.py`), URL configurations (`urls.py`), and WSGI/ASGI configurations.
    *   Configures static and media file handling.

## Building and Running

### Prerequisites

*   Python 3.x
*   `pip` (Python package installer)

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd bizprint
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```
5.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Collect static files (for production or if using Whitenoise):**
    ```bash
    python manage.py collectstatic
    ```
7.  **Run data seeding commands (optional, for development data):**
    ```bash
    python manage.py seed_products
    python manage.py seed_design_packages
    # If other seed commands exist, run them here
    ```

### Running the Development Server

To start the local development server:

```bash
python manage.py runserver
```

The application should be accessible at `http://127.0.0.1:8000/`.

## Development Conventions

*   **Code Structure:** Follows standard Django application structure and best practices.
*   **Slugs:** Uses a custom `UniqueSlugMixin` for automatically generating and managing unique slugs for models like `Product` and `Category`.
*   **Authentication:** Utilizes Django's built-in authentication system, extended with `CustomerProfile`.
*   **Session Management:** Uses Django's session framework to temporarily store pending order data for guest users before login.
*   **Messaging:** Employs Django's messages framework to provide user feedback (e.g., success, error, info messages).
*   **Email Backend:** Configured to use a console email backend in development (`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`) for easy testing of email functionalities. Production setup would require configuring a proper SMTP backend.
*   **Internationalization/Localization:** Configured for `en-us` and `UTC` timezone, with `USE_I18N = True`.

## Testing

The presence of `tests.py` files within applications (`accounts`, `designs`, `products`) indicates that the project is set up with automated tests.
To run tests:
```bash
python manage.py test
```
