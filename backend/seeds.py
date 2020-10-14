from typing import NamedTuple

import click
from flask.cli import with_appcontext
from faker import Faker

from endpoints import registerOperator, register_volunteer, registerBeneficiary
from models import Beneficiary, Cluster, Request, User, Volunteer
from models.enums import Zone, VolunteerRole
from tests.factories import BeneficiaryFactory, ClusterFactory, RequestFactory


class SeedUser(NamedTuple):
    first_name: str
    last_name: str
    roles: list = ["fixer"]


class SeedVolunteer(NamedTuple):
    first_name: str
    last_name: str
    zone: Zone
    address: str
    role: VolunteerRole
    phone: str = None
    status: str = "active"


class SeedBeneficiary(NamedTuple):
    first_name: str
    last_name: str
    zone: Zone
    address: str
    phone: str = None
    is_active: bool = False


@click.command("init-db")
@with_appcontext
def seed_db_command():
    """Clear the existing data and create new tables."""
    User.objects().delete()
    Volunteer.objects().delete()
    Beneficiary.objects().delete()
    Cluster.objects().delete()
    Request.objects().delete()
    fake = Faker()

    users = [
        SeedUser(first_name="Grigore", last_name="Ureche", roles=["admin"],),
        SeedUser(first_name="Ion", last_name="Neculce",),
        SeedUser(first_name="Alexandru", last_name="Donici",),
    ]

    volunteer_list = [
        SeedVolunteer(
            first_name="Serghei",
            last_name="Volkov",
            phone="69000000",
            zone="botanica",
            address="str. Stefan cel Mare 6",
            role="delivery",
        ),
        SeedVolunteer(
            first_name="Valerii",
            last_name="Rever",
            phone="69000001",
            zone="centru",
            address="str. Stefan cel Mare 23",
            role="copilot",
        ),
        SeedVolunteer(
            first_name="Ivan",
            last_name="Cretu",
            phone="69000002",
            zone="riscani",
            address="str. Stefan cel Mare 43",
            role="copilot",
        ),
        SeedVolunteer(
            first_name="Serghei",
            last_name="Breter",
            zone="centru",
            address="str. Stefan cel Mare 43",
            role="copilot",
            status="inactive",
        ),
    ]

    beneficiaries = [
        SeedBeneficiary(first_name="Valerii", last_name="Krisp", phone="79000003", zone="ciocana",
                      address="str. Stefan cel Mare 55", is_active=True),
        SeedBeneficiary(first_name="Ghenadii", last_name="Sidorov", phone="79000005", zone="centru",
                      address="str. Stefan cel Mare 66", is_active=True),
        SeedBeneficiary(first_name="Pavel", last_name="Velikov", phone="79000006", zone="riscani",
                      address="str. Stefan cel Mare 43"),
        SeedBeneficiary(first_name="Denis", last_name="Remerer",  zone="centru",
                      address="str. Stefan cel Mare 43")
    ]

    for user in users:
        registerOperator(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": f"{user.last_name.lower()}@example.com",
                "password": "123456",
                "roles": user.roles,
            },
            "admin",
        )

    volunteers = []
    for volunteer in volunteer_list:
        email = f"{volunteer.last_name.lower()}@example.com"
        volunteer_json = register_volunteer(
            {
                "first_name": volunteer.first_name,
                "last_name": volunteer.last_name,
                "email": email,
                "role": volunteer.role,
                "phone": volunteer.phone,
                "zone": volunteer.zone,
                "address": volunteer.address,
                "status": volunteer.status,
            },
            f"{users[0].last_name.lower()}@example.com",
        )
        click.echo(volunteer_json)
        volunteers.append(Volunteer.objects(email=email).get())

    for beneficiary in beneficiaries:
        beneficiary = registerBeneficiary(
            {
                "first_name": beneficiary.first_name,
                "last_name": beneficiary.last_name,
                "phone": beneficiary.phone,
                "zone": beneficiary.zone,
                "address": beneficiary.address,
                "is_active": beneficiary.is_active
            },
            f"{users[0].last_name.lower()}@example.com"
        )
        click.echo(beneficiary)

    # More beneficiaries ;-)
    beneficiaries = [
        BeneficiaryFactory(
            first_name="Jora",
            last_name="Bricică",
            age=56,
            phone="079034",
            landline="022242424",
            zone="botanica",
            address="bld Decebal 45",
            created_at="2020-01-01",
        ),
        BeneficiaryFactory(
            first_name="Nicolae",
            last_name="Popa",
            age=66,
            phone="79700515",
            landline="022830685",
            zone="botanica",
            address="bld Decebal 560",
            entrance="3",
            floor="3",
            apartment="3",
            special_condition="blind_weak_seer",
            created_at="2020-01-04",
        ),
        BeneficiaryFactory(
            first_name="Vasile",
            last_name="Troscot",
            age=80,
            phone="37378000",
            landline="022835600",
            zone="centru",
            address="str G. Asachi 56",
            entrance="5",
            floor="5",
            apartment="5",
            special_condition="deaf_mute",
            created_at="2020-01-08",
        ),
    ]
    operator = User.objects().first()

    for idx, beneficiary in enumerate(beneficiaries):
        beneficiary.save()

        if idx > 1:  # Only first two beneficiaries have requests
            continue

        cluster = ClusterFactory(volunteer=volunteers[idx])
        cluster.save()

        req = RequestFactory(beneficiary=beneficiary, user=operator, created_at="2020-01-01", comments=fake.paragraph())
        req.save()
        req = RequestFactory(
            beneficiary=beneficiary,
            user=operator,
            type="grocery",
            status="in_process",
            created_at=f"2020-02-0{idx + 1}",
            cluster=cluster,
            comments=fake.paragraph(),
        )
        req.save()
        # Solved request
        req = RequestFactory(
            beneficiary=beneficiary,
            user=operator,
            status="solved",
            created_at=f"2020-03-0{idx + 1}",
            cluster=cluster,
            comments=fake.paragraph(),
        )
        req.save()
        # Canceled request
        req = RequestFactory(
            beneficiary=beneficiary,
            user=operator,
            status="canceled",
            type="medicine",
            created_at=f"2020-04-0{idx + 1}",
            cluster=cluster,
            comments=fake.paragraph(),
        )
        req.save()

        # Archived request
        req = RequestFactory(
            beneficiary=beneficiary,
            user=operator,
            status="archived",
            type="medicine",
            created_at=f"2020-05-0{idx + 1}",
            cluster=cluster,
            comments=fake.paragraph(),
        )
        req.save()

    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(seed_db_command)
