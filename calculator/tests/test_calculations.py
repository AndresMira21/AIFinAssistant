from django.test import TestCase
from decimal import Decimal
from calculator.services.financial_calculations import (
    calculate_npv,
    calculate_irr,
    calculate_compound_interest,
    calculate_amortization,
    fmt8
)

class FinancialCalculationsTest(TestCase):

    def test_npv_positive_and_negative(self):
        # Test case: rate=10%, Initial=-10000, Y1=3000, Y2=4200, Y3=6800
        cashflows = [Decimal("-10000"), Decimal("3000"), Decimal("4200"), Decimal("6800")]
        rate = Decimal("0.10")
        
        # NPV = -10000 + 3000/(1.1)^1 + 4200/(1.1)^2 + 6800/(1.1)^3
        # NPV = -10000 + 2727.272727... + 3471.07438... + 5108.9406...
        # NPV ≈ 1307.28775357
        
        result = calculate_npv(rate, cashflows)
        expected = Decimal("1307.28775357")
        self.assertEqual(result, expected)

    def test_irr_convergence(self):
        # Test case: Initial=-100, Y1=60, Y2=60. 
        # r where NPV=0. 100 = 60/(1+r) + 60/(1+r)^2 -> r = roughly 13.066238629%
        cashflows = [Decimal("-100"), Decimal("60"), Decimal("60")]
        
        result = calculate_irr(cashflows)
        # Check against Newton-Raphson approximation
        expected = Decimal("0.13066239")
        self.assertEqual(result, expected)

    def test_compound_interest(self):
        # Principal 10,000, 5% annual, monthly comp (12), 5 years
        # A = 10000 * (1 + 0.05/12)^(12*5)
        P = Decimal("10000")
        r = Decimal("0.05")
        n = 12
        t = Decimal("5")
        
        result = calculate_compound_interest(P, r, n, t)
        
        # Expected value ≈ 12833.58678504
        expected_amt = Decimal("12833.58678504")
        self.assertEqual(result["amount"], expected_amt)
        self.assertEqual(result["interest_earned"], expected_amt - P)

    def test_amortization_table_sum(self):
        # French amortization: P=1000, r=0.01 (1%), 3 periods
        P = Decimal("1000")
        r = Decimal("0.01")
        periods = 3
        
        result = calculate_amortization(P, r, periods)
        
        # PMT = 1000 * 0.01 / (1 - (1.01)^-3)
        # PMT ≈ 340.02211244
        expected_pmt = Decimal("340.02211244")
        self.assertEqual(result["payment"], expected_pmt)
        
        # Check if the final balance ends at exactly zero
        table = result["table"]
        self.assertEqual(len(table), 3)
        self.assertEqual(table[-1]["balance_end"], Decimal("0.00000000"))
        
        # Check integrity: sum(principal_paid) == P
        sum_principal = sum(Decimal(row["principal_paid"]) for row in table)
        self.assertEqual(fmt8(sum_principal), fmt8(P))
