import factory

from models import Beneficiary, Operator, Request, Cluster, Volunteer
from config import PassHash
from models.enums import RequestStatus, Zone


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
    age = 20
    address = "Botanica"
    zone_address = "Botanica"
    zone = "botanica"
    secret = "G900"
    phone = "11112222"
    offer = "1"
    comments = ""
    urgent = False
    curator = False
    has_disabilities = False
    black_list = False


class VolunteerFactory(factory.Factory):
    class Meta:
        model = Volunteer

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = 50
    email = factory.Faker("email")
    zone = "botanica"
    address = "bld. Decebal 45"
    zone_address = "trululu"


class ClusterFactory(factory.Factory):
    class Meta:
        model = Cluster

    volunteer = factory.SubFactory(VolunteerFactory)


class RequestFactory(factory.Factory):
    class Meta:
        model = Request

    beneficiary = factory.SubFactory(BeneficiaryFactory)
    user = factory.SubFactory(OperatorFactory)
    status = "new"
