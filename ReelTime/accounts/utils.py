from accounts.models import User
from django.contrib.auth.hashers import make_password
import re

def create_default_admin(cinema_name, email):
    # Convert to lowercase, replace spaces with underscores, remove invalid chars
    safe_cinema_name = re.sub(r'[^a-z0-9_]+', '', cinema_name.lower().replace(' ', '_'))

    admin = User.objects.create(
        first_name='Cinema',
        last_name='Admin',
        username=f"{safe_cinema_name}_admin",
        email=email,
        phone_number="00000000000",
        password=make_password('admin123'),
        is_admin=True,
        must_change_password=True,
        cinema_name=cinema_name
    )
    return admin


def get_logged_in_user(request):
    user_id = request.session.get('user_id')
    return User.objects.filter(id=user_id).first()