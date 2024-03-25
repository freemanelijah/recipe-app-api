"""
Django command to wait for the database to be available.
"""

import time

from psycopg2 import OperationalError as Psycopg2OperationalError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entry point for Django command."""
        self.stdout.write('Waiting for database...')
        db_up = False  # Assume DB is down until checked.
        while db_up is False:
            try:
                # This is the check method that we mocked inside tests.
                # If db is not ready, an exception is thrown
                # (Psycopg2OperationalError, OperationalError).
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OperationalError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available. '))
