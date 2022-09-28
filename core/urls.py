# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/',     admin.site.urls),  # Django admin route
    path("",           include("apps.authentication.urls")),  # Auth routes - login / register

    # ADD NEW Routes HERE
    path("api/",       include("apps.api.urls")),            # API Generator Routes
    path('ecommerce/', include('apps.ecommerce.urls')),  # E-Commerce Routes
    path('',           include('apps.dyn_datatables.urls')),  # Dynamic DB Routes

    # Leave `Home.Urls` as last the last line
    path("",           include("apps.home.urls"))  # Generic Routing
]