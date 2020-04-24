import factory

from models import Operator
from config import PassHash


class OperatorFactory(factory.Factory):
    class Meta:
        model = Operator

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = PassHash.hash('123456')
