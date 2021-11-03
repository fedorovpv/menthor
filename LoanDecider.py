import math


class LoanDecider:
    BASE_RATE = 10

    INC_SRC_UNEMPLOYED = 'безработный'
    INC_SRC_HIRED = 'наёмный работник'
    INC_SRC_OWN_BUSINESS = 'собственный бизнес'
    INC_SRC_PASSIVE = 'пассивный доход'

    SEX_MALE = 'M'
    SEX_FEMALE = 'F'

    OBJ_MORTGAGE = 'ипотека'
    OBJ_BUSINESS_IMPROVEMENT = 'развитие бизнеса'
    OBJ_CAR_LOAN = 'автокредит'
    OBJ_CONSUMER_LOAN = 'потребительский'

    MAX_AMOUNT_PER_INCOME_SOURCE = {
        INC_SRC_PASSIVE: 1,
        INC_SRC_HIRED: 5,
        INC_SRC_OWN_BUSINESS: 10
    }

    MAX_AMOUNT_PER_RATING = {
        -1: 1,
        0: 5,
        1: 10,
        2: 10
    }

    MODIFIERS_PER_INCOME_SOURCE = {
        INC_SRC_PASSIVE: 0.5,
        INC_SRC_HIRED: -0.25,
        INC_SRC_OWN_BUSINESS: 0.25
    }

    MODIFIERS_PER_OBJ = {
        OBJ_MORTGAGE: -2,
        OBJ_CAR_LOAN: 0,
        OBJ_BUSINESS_IMPROVEMENT: -0.5,
        OBJ_CONSUMER_LOAN: 1.5
    }

    def __init__(self, age, sex, income_src, income_year, rating, asking_for, time, objective):
        self.age = age
        self.sex = sex
        self.income_src = income_src
        self.income_year = income_year
        self.rating = rating
        self.asking_for = asking_for
        self.time = time
        self.objective = objective

    @property
    def is_not_retired(self):
        return ((self.sex == self.SEX_FEMALE) and (self.age < 60)) or\
               ((self.sex == self.SEX_MALE) and (self.age < 65))

    @property
    def is_income_ok(self):
        return self.asking_for / self.time <= self.income_year / 3

    @property
    def is_rating_ok(self):
        return self.rating > -2

    @property
    def is_source_income_ok(self):
        return self.income_src != self.INC_SRC_UNEMPLOYED

    @property
    def year_payment_is_ok(self):
        return self.income_year / 2 >= self.year_payment

    @property
    def max_amount(self):
        return min(self.MAX_AMOUNT_PER_INCOME_SOURCE[self.income_src], self.MAX_AMOUNT_PER_RATING[self.rating])

    @property
    def modifier_by_ammount(self):
        return -math.log(self.approved_amount, 10)

    @property
    def rate_modifiers(self):
        return self.MODIFIERS_PER_OBJ[self.objective] + self.MODIFIERS_PER_INCOME_SOURCE[self.income_src]\
               + self.modifier_by_ammount

    @property
    def year_payment(self):
        return self.approved_amount * (1 + self.time * self.rate) / self.time

    @property
    def approved_amount(self):
        return min(self.asking_for, self.max_amount)

    @property
    def rate(self):
        return self.BASE_RATE + self.rate_modifiers

    @property
    def approved(self):
        return self.is_not_retired and self.is_income_ok and self.is_rating_ok and self.is_source_income_ok and\
               self.year_payment_is_ok

    def decide(self):
        return self.approved, self.year_payment
