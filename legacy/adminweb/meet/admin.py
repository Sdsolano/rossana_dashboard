from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Config)
admin.site.register(Zoom)
admin.site.register(PayGateway)
admin.site.register(Pay)