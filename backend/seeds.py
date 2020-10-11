from typing import NamedTuple

import click
from flask.cli import with_appcontext

from endpoints import registerOperator
from endpoints import register_volunteer
from endpoints import registerBeneficiary
from models import User
from models import Volunteer
from models import Beneficiary
from models.enums import Zone, VolunteerRole


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

    users = [
        SeedUser(first_name="Grigore", last_name="Ureche", roles=["admin"],),
        SeedUser(first_name="Ion", last_name="Neculce",),
        SeedUser(first_name="Alexandru", last_name="Donici",),
    ]

    volunteers = [
        SeedVolunteer(first_name="Serghei", last_name="Volkov", phone="69000000", zone="Botanica",
                      address="str. Stefan cel Mare 6", role='delivery'),
        SeedVolunteer(first_name="Valerii", last_name="Rever", phone="69000001", zone="Centru",
                      address="str. Stefan cel Mare 23", role='copilot'),
        SeedVolunteer(first_name="Ivan", last_name="Cretu", phone="69000002", zone="Riscani",
                      address="str. Stefan cel Mare 43", role='copilot'),
        SeedVolunteer(first_name="Serghei", last_name="Breter",  zone="Centru",
                      address="str. Stefan cel Mare 43", role='copilot', status="inactive")
    ]

    beneficiaries = [
        SeedBeneficiary(first_name="Valerii", last_name="Krisp", phone="79000003", zone="Ciocana",
                      address="str. Stefan cel Mare 55", is_active=True),
        SeedBeneficiary(first_name="Ghenadii", last_name="Sidorov", phone="79000005", zone="Centru",
                      address="str. Stefan cel Mare 66", is_active=True),
        SeedBeneficiary(first_name="Pavel", last_name="Velikov", phone="79000006", zone="Riscani",
                      address="str. Stefan cel Mare 43"),
        SeedBeneficiary(first_name="Denis", last_name="Remerer",  zone="Centru",
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

    for volunteer in volunteers:
        volunteer = register_volunteer(
            {
                "first_name": volunteer.first_name,
                "last_name": volunteer.last_name,
                "email": f"{volunteer.last_name.lower()}@example.com",
                "role": volunteer.role,
                "phone": volunteer.phone,
                "zone": volunteer.zone,
                "address": volunteer.address,
                "status": volunteer.status
            },
            f"{users[0].last_name.lower()}@example.com"
        )
        click.echo(volunteer)

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

    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(seed_db_command)
