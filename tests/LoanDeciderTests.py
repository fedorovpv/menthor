import pytest
import math
from LoanDecider import LoanDecider


def expected_year_amount(amount, years, rate):
    """Auxiliary function to count year amount;"""
    return amount * (1 + years * (rate - math.log(amount, 10)) / 100) / years


class TestLoanDecider:
    """Tests for Loan Decider"""
    @staticmethod
    def get_config(age=20, sex=LoanDecider.SEX_MALE, income_src=LoanDecider.INC_SRC_OWN_BUSINESS,
                   income_year=100, rating=2, asking_for=1, years=1, objective=LoanDecider.OBJ_CAR_LOAN):
        """
        Getting base config for ordinary man with the most simple characteristics for loan. By  default, objective
         is car loan for 0 modifier, rating and income are at max, term of loan is 1 for simplifying. Rate is Base 10
         plus 0.25 for 'own business'
        """
        return {'age': age, 'sex': sex, 'income_src': income_src, 'income_year': income_year, 'rating': rating,
                'asking_for': asking_for, 'years': years, 'objective': objective}

    @pytest.mark.parametrize(
        'message, exp_approved, params', [
            ('Basic config, test should be successful for the precision of further tests.', True, {}),
            ('Unemployed person.', False, {'income_src': LoanDecider.INC_SRC_UNEMPLOYED}),
            ('Male retired.', False, {'age': 65}),
            ('Male almost retired.', True, {'age': 64}),
            ('Female retired.', False, {'age': 60, 'sex': LoanDecider.SEX_FEMALE}),
            ('Female almost retired.', True, {'age': 59, 'sex': LoanDecider.SEX_FEMALE}),
            ('Low rating.', False, {'rating': -2}),
            ('Rating is OK: -1.', True, {'rating': -1}),
            ('Rating is OK: 0.', True, {'rating': 0}),
            ('Rating is OK: 1.', True, {'rating': 1}),
            ('Rating is OK: 2.', True,  {'rating': 2}),
            ('Amount without percentage is huge, but still OK. Asking_for / years == year_income / 3.', True,
             {'asking_for': 1, 'years': 1, 'income_year': 3}),
            ('Amount without percentage is huge. Asking_for / years > year_income / 3.', False,
             {'asking_for': 1.0001, 'years': 1, 'income_year': 3})
        ])
    def test_approve(self, message, exp_approved, params):
        """Testing approval for loan"""
        config = self.get_config(**params)
        loan_decider = LoanDecider(**config)
        approved, year_payment = loan_decider.decide()
        if exp_approved:   # we are testing approvement, not payment, so if it's None when loan is approved -- ok, None otherwise
            year_payment_is_ok = year_payment is not None
        else:
            year_payment_is_ok = year_payment is None

        assert (exp_approved == approved) and year_payment_is_ok,\
            message + f"\nExpected approve: {exp_approved}, actual: {approved};\n" \
                      f"Year payment: {year_payment}.\nConfig: {config}"

    @pytest.mark.parametrize(
        'message, exp_year_payment, params', [
            ('Passive income', expected_year_amount(amount=1, years=1, rate=10.5),
             {'income_src': LoanDecider.INC_SRC_PASSIVE, 'asking_for': LoanDecider.MAX_AMOUNT_PER_INCOME_SOURCE[LoanDecider.INC_SRC_PASSIVE]}),

            ('Hired income,', expected_year_amount(amount=5, years=1, rate=9.75),
             {'income_src': LoanDecider.INC_SRC_HIRED, 'asking_for': LoanDecider.MAX_AMOUNT_PER_INCOME_SOURCE[LoanDecider.INC_SRC_HIRED]}),

            ('Own business income', expected_year_amount(amount=10, years=1, rate=10.25),
             {'income_src': LoanDecider.INC_SRC_OWN_BUSINESS, 'asking_for': LoanDecider.MAX_AMOUNT_PER_INCOME_SOURCE[LoanDecider.INC_SRC_OWN_BUSINESS]}),

            ('Rating -1', expected_year_amount(amount=1, years=1, rate=10.25), {'rating': -1, 'asking_for': LoanDecider.MAX_AMOUNT_PER_RATING[-1]}),
            ('Rating 0', expected_year_amount(amount=5, years=1, rate=10.25), {'rating': 0, 'asking_for': LoanDecider.MAX_AMOUNT_PER_RATING[0]}),
            ('Rating 1', expected_year_amount(amount=10, years=1, rate=10.25), {'rating': 1, 'asking_for': LoanDecider.MAX_AMOUNT_PER_RATING[1]}),
            ('Rating 2', expected_year_amount(amount=10, years=1, rate=10.25), {'rating': 2, 'asking_for': LoanDecider.MAX_AMOUNT_PER_RATING[2]})
        ])
    def test_border_values_max_amount(self, message, exp_year_payment, params):
        """Testing border values, max and a bit more."""
        config = self.get_config(**params)
        loan_decider = LoanDecider(**config)
        approved, year_payment = loan_decider.decide()
        assert approved and (exp_year_payment == year_payment),\
            message + f" Max amount but still OK. \nExpected approve: True, actual: {approved};\n" \
                      f"Expected year payment: {exp_year_payment}, actual: {year_payment}.\nConfig: {config}"

        config['asking_for'] += 0.01
        loan_decider = LoanDecider(**config)
        approved, year_payment = loan_decider.decide()
        assert approved and (exp_year_payment == year_payment), \
            message + f"More than max amount\nExpected approve: True, actual: {approved};\n" \
                      f"Expected year payment: {exp_year_payment}, actual: {year_payment}.\nConfig: {config}"

    @pytest.mark.parametrize(
        'message, exp_year_payment, params', [
            ('Modifiers changing. Objective: Car Loan', expected_year_amount(amount=1, years=1, rate=10.25), {}),
            ('Modifiers changing. Objective: Mortgage', expected_year_amount(amount=1, years=1, rate=8.25), {'objective': LoanDecider.OBJ_MORTGAGE}),
            ('Modifiers changing. Objective: Business Improvement', expected_year_amount(amount=1, years=1, rate=9.75), {'objective': LoanDecider.OBJ_BUSINESS_IMPROVEMENT}),
            ('Modifiers changing. Objective: Consumer Loan', expected_year_amount(amount=1, years=1, rate=11.75), {'objective': LoanDecider.OBJ_CONSUMER_LOAN}),
            ('Modifiers changing. Small amount', expected_year_amount(amount=0.1, years=1, rate=10.25), {'asking_for': 0.1}),
            ('Modifiers changing. Huge amount', expected_year_amount(amount=10, years=1, rate=10.25), {'asking_for': 10}),
            ('Time changes year payment as expected', expected_year_amount(amount=1, years=20, rate=10.25), {'years': 20}),
        ])
    def test_modifiers(self, message, exp_year_payment, params):
        """Testing year amount."""
        config = self.get_config(**params)
        loan_decider = LoanDecider(**config)
        approved, year_payment = loan_decider.decide()
        assert approved and (exp_year_payment == year_payment), \
            message + f"\nExpected approve: True, actual: {approved};\n" \
                      f"Expected year payment: {exp_year_payment}, actual: {year_payment}.\nConfig: {config}"
