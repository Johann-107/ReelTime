from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect


def admin_required(view_func):
    """
    Restricts access to admin users only.
    Redirects non-admins to user_dashboard.
    Redirects unauthenticated users to login.
    """
    decorated_view_func = login_required(
        user_passes_test(
            lambda u: u.is_admin,           # condition: must be admin
            login_url='user_dashboard'      # if not admin
        )(view_func)
    )
    return decorated_view_func
