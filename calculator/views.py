"""
views.py — Calculator App
--------------------------
Handles GET (show form) and POST (compute and show result) for each calculator.
All calculation errors are caught and shown as form errors.
"""

from django.shortcuts import render
from .forms import NPVForm, IRRForm, CompoundInterestForm, AmortizationForm
from .services.financial_calculations import (
    calculate_npv,
    calculate_irr,
    calculate_compound_interest,
    calculate_amortization,
)


def index(request):
    """Main calculator page — shows all four calculators in a tabbed interface."""
    npv_form = NPVForm()
    irr_form = IRRForm()
    ci_form = CompoundInterestForm()
    amort_form = AmortizationForm()

    context = {
        "npv_form": npv_form,
        "irr_form": irr_form,
        "ci_form": ci_form,
        "amort_form": amort_form,
        "active_tab": "npv",
    }
    return render(request, "calculator/index.html", context)


def npv_view(request):
    """Process NPV calculation."""
    npv_form = NPVForm(request.POST or None)
    irr_form = IRRForm()
    ci_form = CompoundInterestForm()
    amort_form = AmortizationForm()
    result = None
    error = None

    if request.method == "POST" and npv_form.is_valid():
        try:
            rate = npv_form.cleaned_data["rate"]
            cashflows = npv_form.cleaned_data["cashflows"]
            npv_result = calculate_npv(rate, cashflows)
            result = {
                "value": npv_result,
                "rate": rate,
                "cashflows": cashflows,
                "interpretation": (
                    "✅ Proyecto VIABLE: el VAN es positivo."
                    if npv_result > 0
                    else "❌ Proyecto NO VIABLE: el VAN es negativo o cero."
                ),
            }
        except ValueError as e:
            error = str(e)

    return render(
        request,
        "calculator/index.html",
        {
            "npv_form": npv_form,
            "irr_form": irr_form,
            "ci_form": ci_form,
            "amort_form": amort_form,
            "npv_result": result,
            "npv_error": error,
            "active_tab": "npv",
        },
    )


def irr_view(request):
    """Process IRR calculation."""
    npv_form = NPVForm()
    irr_form = IRRForm(request.POST or None)
    ci_form = CompoundInterestForm()
    amort_form = AmortizationForm()
    result = None
    error = None

    if request.method == "POST" and irr_form.is_valid():
        try:
            cashflows = irr_form.cleaned_data["cashflows"]
            irr_result = calculate_irr(cashflows)
            result = {
                "value": irr_result,
                "cashflows": cashflows,
                "percentage": irr_result * 100,
            }
        except ValueError as e:
            error = str(e)

    return render(
        request,
        "calculator/index.html",
        {
            "npv_form": npv_form,
            "irr_form": irr_form,
            "ci_form": ci_form,
            "amort_form": amort_form,
            "irr_result": result,
            "irr_error": error,
            "active_tab": "irr",
        },
    )


def compound_interest_view(request):
    """Process Compound Interest calculation."""
    npv_form = NPVForm()
    irr_form = IRRForm()
    ci_form = CompoundInterestForm(request.POST or None)
    amort_form = AmortizationForm()
    result = None
    error = None

    if request.method == "POST" and ci_form.is_valid():
        try:
            result = calculate_compound_interest(
                principal=ci_form.cleaned_data["principal"],
                annual_rate=ci_form.cleaned_data["annual_rate"],
                n_per_year=ci_form.cleaned_data["n_per_year"],
                years=ci_form.cleaned_data["years"],
            )
        except ValueError as e:
            error = str(e)

    return render(
        request,
        "calculator/index.html",
        {
            "npv_form": npv_form,
            "irr_form": irr_form,
            "ci_form": ci_form,
            "amort_form": amort_form,
            "ci_result": result,
            "ci_error": error,
            "active_tab": "compound",
        },
    )


def amortization_view(request):
    """Process French-method amortization table."""
    npv_form = NPVForm()
    irr_form = IRRForm()
    ci_form = CompoundInterestForm()
    amort_form = AmortizationForm(request.POST or None)
    result = None
    error = None

    if request.method == "POST" and amort_form.is_valid():
        try:
            result = calculate_amortization(
                principal=amort_form.cleaned_data["principal"],
                monthly_rate=amort_form.cleaned_data["monthly_rate"],
                periods=amort_form.cleaned_data["periods"],
            )
        except ValueError as e:
            error = str(e)

    return render(
        request,
        "calculator/index.html",
        {
            "npv_form": npv_form,
            "irr_form": irr_form,
            "ci_form": ci_form,
            "amort_form": amort_form,
            "amort_result": result,
            "amort_error": error,
            "active_tab": "amortization",
        },
    )
