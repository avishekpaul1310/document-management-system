from django.utils import timezone

def session_info(request):
    return {
        'current_time': timezone.now(),
    }