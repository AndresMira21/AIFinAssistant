"""
forms.py — Calculator App
--------------------------
Django forms for each financial calculation.
All inputs are validated as strings that can be converted to Decimal.
"""

from django import forms
from decimal import Decimal, InvalidOperation


def parse_cashflows(text: str):
    """Parse a newline/comma-separated list of cash flow values into Decimals."""
    raw = text.replace(",", "\n").split()
    cashflows = []
    for item in raw:
        item = item.strip()
        if not item:
            continue
        try:
            cashflows.append(Decimal(item))
        except InvalidOperation:
            raise forms.ValidationError(
                f"'{item}' no es un número válido para un flujo de caja."
            )
    return cashflows


class NPVForm(forms.Form):
    rate = forms.CharField(
        label="Tasa de descuento (ej: 0.10 para 10%)",
        widget=forms.TextInput(attrs={"placeholder": "0.10", "class": "form-input"}),
    )
    cashflows = forms.CharField(
        label="Flujos de caja (uno por línea o separados por coma)",
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "-10000\n3000\n4000\n5000\n2000",
                "class": "form-input",
            }
        ),
    )

    def clean_rate(self):
        raw = self.cleaned_data["rate"].strip()
        try:
            rate = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("La tasa debe ser un número decimal válido.")
        if rate <= Decimal("-1"):
            raise forms.ValidationError("La tasa debe ser mayor que -1.")
        return rate

    def clean_cashflows(self):
        raw = self.cleaned_data["cashflows"]
        cfs = parse_cashflows(raw)
        if not cfs:
            raise forms.ValidationError("Debe ingresar al menos un flujo de caja.")
        return cfs


class IRRForm(forms.Form):
    cashflows = forms.CharField(
        label="Flujos de caja (uno por línea o separados por coma)",
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "-10000\n3000\n4000\n5000\n2000",
                "class": "form-input",
            }
        ),
    )

    def clean_cashflows(self):
        raw = self.cleaned_data["cashflows"]
        cfs = parse_cashflows(raw)
        if len(cfs) < 2:
            raise forms.ValidationError(
                "Se requieren al menos 2 flujos de caja para calcular la TIR."
            )
        has_positive = any(cf > 0 for cf in cfs)
        has_negative = any(cf < 0 for cf in cfs)
        if not (has_positive and has_negative):
            raise forms.ValidationError(
                "Los flujos deben tener al menos un valor positivo y uno negativo."
            )
        return cfs


class CompoundInterestForm(forms.Form):
    FREQUENCY_CHOICES = [
        ("1", "Anual"),
        ("2", "Semestral"),
        ("4", "Trimestral"),
        ("12", "Mensual"),
        ("52", "Semanal"),
        ("365", "Diaria"),
    ]

    principal = forms.CharField(
        label="Capital inicial (P)",
        widget=forms.TextInput(attrs={"placeholder": "10000.00", "class": "form-input"}),
    )
    annual_rate = forms.CharField(
        label="Tasa anual (ej: 0.05 para 5%)",
        widget=forms.TextInput(attrs={"placeholder": "0.05", "class": "form-input"}),
    )
    n_per_year = forms.ChoiceField(
        label="Frecuencia de capitalización",
        choices=FREQUENCY_CHOICES,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    years = forms.CharField(
        label="Tiempo (años)",
        widget=forms.TextInput(attrs={"placeholder": "5", "class": "form-input"}),
    )

    def clean_principal(self):
        raw = self.cleaned_data["principal"].strip()
        try:
            val = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("El capital debe ser un número válido.")
        if val <= Decimal("0"):
            raise forms.ValidationError("El capital debe ser mayor que cero.")
        return val

    def clean_annual_rate(self):
        raw = self.cleaned_data["annual_rate"].strip()
        try:
            val = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("La tasa debe ser un número decimal válido.")
        if val <= Decimal("-1"):
            raise forms.ValidationError("La tasa debe ser mayor que -1.")
        return val

    def clean_n_per_year(self):
        return int(self.cleaned_data["n_per_year"])

    def clean_years(self):
        raw = self.cleaned_data["years"].strip()
        try:
            val = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("El tiempo debe ser un número válido.")
        if val <= Decimal("0"):
            raise forms.ValidationError("El tiempo debe ser mayor que cero.")
        return val


class AmortizationForm(forms.Form):
    principal = forms.CharField(
        label="Monto del préstamo",
        widget=forms.TextInput(attrs={"placeholder": "100000.00", "class": "form-input"}),
    )
    monthly_rate = forms.CharField(
        label="Tasa de interés por período (ej: 0.01 para 1%)",
        widget=forms.TextInput(attrs={"placeholder": "0.01", "class": "form-input"}),
    )
    periods = forms.IntegerField(
        label="Número de períodos",
        widget=forms.NumberInput(attrs={"placeholder": "36", "class": "form-input"}),
        min_value=1,
        max_value=600,
    )

    def clean_principal(self):
        raw = self.cleaned_data["principal"].strip()
        try:
            val = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("El monto debe ser un número válido.")
        if val <= Decimal("0"):
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return val

    def clean_monthly_rate(self):
        raw = self.cleaned_data["monthly_rate"].strip()
        try:
            val = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError("La tasa debe ser un número decimal válido.")
        if val <= Decimal("0"):
            raise forms.ValidationError(
                "La tasa por período debe ser mayor que cero. "
                "Para tasa anual del 12%, ingrese 0.01 (mensual)."
            )
        return val
