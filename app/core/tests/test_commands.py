"""
Test custom Django commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# Decorator is the command that we would be mocking. check method inside
# command is the mocked object.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    # patched_check,
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for the database if database is ready."""
        patched_check.return_value = True
        call_command('wait_for_db')
        # ensures that we can make a call to the check object.
        patched_check.assert_called_once_with(databases=['default'])

    # Argument order matters. patched_sleep is first agument because
    # it's looking at the closed decorator. Objects defined at the
    # class level pass into the argument at the end.
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting OperationError."""
        # Attempting to raise an exception if the db is not ready.
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
