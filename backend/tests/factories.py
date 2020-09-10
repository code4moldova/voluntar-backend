import factory

from models import Beneficiary, Operator
from config import PassHash


class OperatorFactory(factory.Factory):
    class Meta:
        model = Operator

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = PassHash.hash("123456")


class BeneficiaryFactory(factory.Factory):
    class Meta:
        model = Beneficiary

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = PassHash.hash("123456")
    age = 20
    address = "Botanica"
    zone_address = "Botanica"
    secret = "G900"
    phone = 11112222
    address = "B"
    zone_address = "A"
    age = "1"
    offer = "1"
    comments = ""
    urgent = False
    curator = False
    has_disabilities = False
    black_list = False
