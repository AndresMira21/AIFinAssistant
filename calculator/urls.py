"""
urls.py — Calculator App
"""

from django.urls import path
from . import views

app_name = "calculator"

urlpatterns = [
    path("", views.index, name="index"),
    path("npv/", views.npv_view, name="npv"),
    path("irr/", views.irr_view, name="irr"),
    path("compound/", views.compound_interest_view, name="compound"),
    path("amortization/", views.amortization_view, name="amortization"),
]
