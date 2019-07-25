'''Random toke generator'''
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    '''Generates a random token'''
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.username)

ACCOUNT_ACTIVATION_TOKEN = AccountActivationTokenGenerator()
