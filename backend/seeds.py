from typing import NamedTuple

import click
from flask.cli import with_appcontext

from endpoints import registerOperator
from models.volunteer_model import User


class SeedUser(NamedTuple):
    first_name: str
    last_name: str
    roles: list = ["fixer"]


@click.command("init-db")
@with_appcontext
def seed_db_command():
    """Clear the existing data and create new tables."""
    User.objects().delete()

    users = [
        SeedUser(first_name="Grigore", last_name="Ureche", roles=["admin"],),
        SeedUser(first_name="Ion", last_name="Neculce",),
        SeedUser(first_name="Alexandru", last_name="Donici",),
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
    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(seed_db_command)
