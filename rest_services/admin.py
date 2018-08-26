from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Batch

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(Batch)
