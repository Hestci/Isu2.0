from ..models import Profile

def user_roles(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return {
            'is_admin': request.user.profile.roles.filter(name='admin').exists(),
            'user_roles': request.user.profile.roles.all()
        }
    return {
        'is_admin': False,
        'user_roles': []
    } 