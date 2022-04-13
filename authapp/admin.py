from django.contrib import admin
from authapp.models import User, PassOtp, UserActivation

# Register your models here.
admin.site.register(User)
admin.site.register(PassOtp)
admin.site.register(UserActivation)