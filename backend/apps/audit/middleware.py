from .models import AuditLog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, resource_type, resource_id='',
               before_state=None, after_state=None):
    merchant = None
    actor = None
    if request.user and request.user.is_authenticated:
        actor = request.user
        try:
            merchant = request.user.merchant
        except Exception:
            pass
    AuditLog.log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        merchant=merchant,
        actor=actor,
        before_state=before_state,
        after_state=after_state,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
