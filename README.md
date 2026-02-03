# VayamTube (YouTube Clone)

A Django-based video sharing platform (VayamTube) built for learning and portfolio purposes.


## Tests & CI
- Tests are run via Django's test runner. Use `python manage.py test`.
- A GitHub Actions workflow runs tests and linting on push.

## Notes
- Media files are ignored by Git and stored in `media/` locally. Use S3 or other storage in production.
- Use `.env` for environment variables and never commit secrets.
