# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
import uuid


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    brand = models.CharField(max_length=100)
    partner = models.CharField(max_length=100, default = 'Gemal')


