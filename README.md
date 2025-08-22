# Multi-Purpose Business Application

A comprehensive Django-based business management system that handles invoices, receipts, waybills, job orders, quotations, expenses, inventory, clients, and accounting.

## Features

- **Invoice Management**: Create, edit, and manage invoices with PDF generation
- **Receipt Management**: Track payments and generate receipts
- **Waybill System**: Manage shipping and delivery documentation
- **Job Orders**: Track and manage work orders
- **Quotations**: Create and manage customer quotes
- **Expense Tracking**: Monitor business expenses
- **Inventory Management**: Track stock levels and products
- **Client Management**: Maintain customer database
- **Accounting**: Basic accounting and financial tracking
- **User Management**: Multi-user system with role-based access

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (Railway) / SQLite (Local)
- **Frontend**: Bootstrap 5, Material Dashboard
- **PDF Generation**: ReportLab, xhtml2pdf
- **API**: Django REST Framework
- **Deployment**: Railway

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd multi_purpose_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DEBUG_INVENTORY=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and go to `http://127.0.0.1:8000`

## Deployment on Railway

This application is configured for deployment on Railway. The deployment process is automated and includes:

- PostgreSQL database provisioning
- Static file serving with WhiteNoise
- Environment variable management
- Automatic builds and deployments

### Railway Deployment Steps

1. **Connect to Railway**
   - Install Railway CLI: `npm install -g @railway/cli`
   - Login: `railway login`

2. **Deploy the application**
   ```bash
   railway init
   railway up
   ```

3. **Set environment variables**
   ```bash
   railway variables set SECRET_KEY=your-production-secret-key
   railway variables set DEBUG=False
   ```

4. **Run migrations**
   ```bash
   railway run python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

## Project Structure

```
multi_purpose_app/
├── apps/                    # Django applications
│   ├── accounts/           # User management
│   ├── accounting/         # Accounting features
│   ├── clients/            # Client management
│   ├── core/               # Core functionality
│   ├── expenses/           # Expense tracking
│   ├── inventory/          # Inventory management
│   ├── invoices/           # Invoice management
│   ├── job_orders/         # Job order tracking
│   ├── quotations/         # Quotation management
│   ├── receipts/           # Receipt management
│   └── waybills/           # Waybill system
├── business_app/           # Main Django project
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
├── Procfile               # Railway deployment configuration
└── runtime.txt            # Python version specification
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the GitHub repository.
