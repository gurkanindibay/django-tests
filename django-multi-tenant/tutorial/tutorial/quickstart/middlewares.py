from django_multitenant.utils import set_current_tenant
from .models import Account
    
class MultitenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Middleware executed")
        if request.user and not request.user.is_anonymous:
            print("Middleware executed with user")
            account = Account.objects.filter(user=request.user).first()
            set_current_tenant(account)
            print("Set tenant to {}".format(account))
        return self.get_response(request)