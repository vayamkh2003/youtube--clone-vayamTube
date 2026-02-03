# VayamTube (YouTube Clone)

A Django-based video sharing platform (VayamTube) built for learning and portfolio purposes.

## Quickstart

1. Clone the repo
2. Create and activate a virtualenv
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and set `SECRET_KEY` and other values
5. Run migrations and collect static files:
   ```bash
   python manage.py migrate
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Tests & CI
- Tests are run via Django's test runner. Use `python manage.py test`.
- A GitHub Actions workflow runs tests and linting on push.

## Notes
- Media files are ignored by Git and stored in `media/` locally. Use S3 or other storage in production.
- Use `.env` for environment variables and never commit secrets.
