from typing import NamedTuple

import click
from flask.cli import with_appcontext

from endpoints import registerOperator
from endpoints import register_volunteer
from models import User
from models import Volunteer
from models.enums import Zone, VolunteerRole


class SeedUser(NamedTuple):
    first_name: str
    last_name: str
    roles: list = ["fixer"]


class SeedVolunteer(NamedTuple):
    first_name: str
    last_name: str
    phone: str
    zone: Zone
    address: str
    role: VolunteerRole
    zone_address: str
    status: str = "active"


@click.command("init-db")
@with_appcontext
def seed_db_command():
    """Clear the existing data and create new tables."""
    User.objects().delete()
    Volunteer.objects().delete()

    users = [
        SeedUser(first_name="Grigore", last_name="Ureche", roles=["admin"],),
        SeedUser(first_name="Ion", last_name="Neculce",),
        SeedUser(first_name="Alexandru", last_name="Donici",),
    ]

    volunteers = [
        SeedVolunteer(first_name="Serghei", last_name="Volkov", phone="373000000000", zone="Botanica",
                      address="str. Stefan cel Mare 6", role='delivery', zone_address="no address"),
        SeedVolunteer(first_name="Valerii", last_name="Rever", phone="(373)033000000", zone="Centru",
                      address="str. Stefan cel Mare 23", role='copilot', zone_address="no address"),
        SeedVolunteer(first_name="Ivan", last_name="Cretu", phone="+373 6044332", zone="Riscani",
                      address="str. Stefan cel Mare 43", role='copilot', zone_address="no address"),
        SeedVolunteer(first_name="Serghei", last_name="Breter", phone="3735454554", zone="Centru",
                      address="str. Stefan cel Mare 43", role='copilot', zone_address="no address", status="inactive")
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
                "zone_address": volunteer.zone_address,
                "status": volunteer.status
            },
            f"{users[0].last_name.lower()}@example.com"
        )
        click.echo(volunteer)

    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(seed_db_command)
