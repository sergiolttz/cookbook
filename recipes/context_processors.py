from .models import UserProfile

def user_profile_header(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return {'logged_in_user_profile': user_profile}
        except UserProfile.DoesNotExist:
            return {'logged_in_user_profile': None}
    return {'logged_in_user_profile': None}