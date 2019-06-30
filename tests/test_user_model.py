import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password = 'Cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_passwrod_getter(self):
        u = User(password = 'Cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'Cat')
        self.assertTrue(u.verify_password('Cat'))
        self.assertFalse(u.verify_password('Dog'))

    def test_password_salts_are_random(self):
        u = User(password = 'Cat')
        u2 = User(password = 'Cat')
        self.assertNotEqual(u.password_hash, u2.password_hash)