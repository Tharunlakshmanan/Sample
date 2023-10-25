# in this file going to generate the token
# make sure the six module installation based on the django documentation
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class TokenGenarator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_active))
genarate_token=TokenGenarator()