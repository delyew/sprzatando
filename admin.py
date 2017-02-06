from django.contrib import admin
from .models import Offer, SignedWorker, Rank

# Register your models here.
admin.site.register(Offer)
admin.site.register(SignedWorker)
admin.site.register(Rank)