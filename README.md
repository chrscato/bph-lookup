# Medicare Rate Lookup Tool

A Django-based tool for looking up Medicare rates based on ZIP codes and CPT codes.
It also supports a Workers' Compensation fee schedule lookup by state and CPT code.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd bph-lookup
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
   - Copy `bph_lookup/settings_template.py` to `bph_lookup/settings.py`
   - Update the `SECRET_KEY` in settings.py
   - Place your `compensation_rates.db` file in the project root directory

5. Run migrations:
```bash
python manage.py migrate
```

6. Collect static files:
```bash
python manage.py collectstatic
```

7. Run the development server:
```bash
python manage.py runserver
```

## Database Structure

The application uses the following tables:
- medicare_locality_map: Maps ZIP codes to locality codes
- medicare_locality_meta: Contains metadata about Medicare localities
- cms_gpci: Geographic Practice Cost Indices
- cms_rvu: Relative Value Units
- cms_conversion_factor: Yearly conversion factors

## Development

- The main lookup view is in `core/views.py`
- Templates are in `core/templates/`
- Static files are in `core/static/`
- Forms are defined in `core/forms.py`

## Security Notes

- Never commit the actual `compensation_rates.db` file
- Keep your `settings.py` file secure and never commit it
- Use environment variables for sensitive data in production

## License

[Your License Here] 