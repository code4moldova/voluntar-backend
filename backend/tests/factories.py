import factory

from models import Beneficiary, Operator, Request, Cluster, Volunteer, Notification
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
    age = 20
    address = "Botanica"
    zone = "botanica"
    phone = "11112222"


class VolunteerFactory(factory.Factory):
    class Meta:
        model = Volunteer

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = "50"
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
    type = "warm_lunch"
    status = "new"
    number = factory.Sequence(lambda n: n + 3500)


class NotificationFactory(factory.Factory):
    class Meta:
        model = Notification

    request = factory.SubFactory(RequestFactory)
    type = "new_request"
    subject = factory.Faker("subject")
