# Admin Scripts

Administrative scripts for database and user management.

## Available Scripts

- **`create_demo_accounts.py`** - Create demo student, teacher, and admin accounts
- **`create_production_superuser.py`** - Create production superuser account
- **`reset_admin_password.py`** - Reset admin user password
- **`reset_migrations.py`** - Reset database migrations (use with caution)

## Usage

Run from project root:
```bash
python scripts/admin/create_demo_accounts.py
```

## Warning

⚠️ These scripts modify the database. Use with caution, especially in production.

