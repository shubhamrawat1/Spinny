from django.contrib import admin
from test_task.models import *


# Registering model so that they can show in admin panel
admin.site.register(Box)
admin.site.register(Store)