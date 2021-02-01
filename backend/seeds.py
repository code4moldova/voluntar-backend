import random
from typing import NamedTuple

import click
from faker import Faker
from flask.cli import with_appcontext

from endpoints import register_volunteer, registerBeneficiary, registerOperator
from models import Beneficiary, Cluster, Notification, NotificationUser, Request, User, Volunteer
from models.enums import VolunteerRole, Zone
from tests.factories import BeneficiaryFactory, ClusterFactory, NotificationFactory, RequestFactory


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
    availability_days: list = ["monday"]
    phone: str = None
    status: str = "active"


class SeedBeneficiary(NamedTuple):
    first_name: str
    last_name: str
    zone: Zone
    address: str
    longitude: float
    latitude: float
    phone: str = None
    landline: str = None
    is_active: bool = False


@click.command("init-db")
@with_appcontext
def seed_db_command():

    if config.FLASK_ENV == "development":
        """Clear the existing data and create new tables."""
        User.objects().delete()
        Volunteer.objects().delete()
        Beneficiary.objects().delete()
        Cluster.objects().delete()
        Request.objects().delete()
        Notification.objects().delete()
        NotificationUser.objects().delete()
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
                phone="68000000",
                zone="botanica",
                address="str. Stefan cel Mare 6",
                role="delivery",
                availability_days=["tuesday"],
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
                availability_days=["tuesday", "friday"],
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
            SeedBeneficiary(
                first_name="Valerii",
                last_name="Krisp",
                phone="79000003",
                zone="ciocana",
                address="Bulevardul Dacia 44",
                is_active=True,
                landline="22022022",
                longitude=28.868399974363115,
                latitude=47.9774200287918,
            ),
            SeedBeneficiary(
                first_name="Ghenadii",
                last_name="Sidorov",
                phone="79000005",
                zone="centru",
                address="Strada Albisoara 44",
                is_active=True,
                landline="22024025",
                longitude=28.845019996559724,
                latitude=47.03426001926646,
            ),
            SeedBeneficiary(
                first_name="Pavel",
                last_name="Velikov",
                phone="79000006",
                zone="riscani",
                address="str. Stefan cel Mare 43",
                longitude=28.845019996559724,
                latitude=47.03426001126646,
            ),
            SeedBeneficiary(
                first_name="Denis",
                last_name="Remerer",
                zone="centru",
                address="str. Stefan cel Mare 43",
                longitude=28.845019996559724,
                latitude=47.03426007926646,
            ),
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
                    "role": [volunteer.role],
                    "phone": volunteer.phone,
                    "zone": volunteer.zone,
                    "address": volunteer.address,
                    "status": volunteer.status,
                    "availability_days": volunteer.availability_days,
                },
                f"{users[0].last_name.lower()}@example.com",
            )
            # print(volunteer_json[0].json)
            click.echo(volunteer_json)
            volunteers.append(Volunteer.objects(email=email).get())

        for beneficiary in beneficiaries:
            beneficiary = registerBeneficiary(
                {
                    "first_name": beneficiary.first_name,
                    "last_name": beneficiary.last_name,
                    "phone": beneficiary.phone,
                    "landline": beneficiary.landline,
                    "zone": beneficiary.zone,
                    "address": beneficiary.address,
                    "is_active": beneficiary.is_active,
                    "latitude": beneficiary.latitude,
                    "longitude": beneficiary.longitude,
                },
                f"{users[0].last_name.lower()}@example.com",
            )
            click.echo(beneficiary)

        # More beneficiaries ;-)
        beneficiaries = [
            BeneficiaryFactory(
                first_name="Jora",
                last_name="Bricică",
                age=56,
                phone="79779034",
                landline="22242424",
                zone="botanica",
                address="bld Decebal 45",
                created_at="2020-01-01",
                longitude=28.865019996559724,
                latitude=47.03421007926646,
            ),
            BeneficiaryFactory(
                first_name="Nicolae",
                last_name="Popa",
                age=66,
                phone="79700515",
                landline="22830685",
                zone="botanica",
                address="bld Decebal 560",
                entrance="3",
                floor="3",
                apartment="3",
                special_condition="blind_weak_seer",
                created_at="2020-01-04",
                longitude=28.845011996559724,
                latitude=47.03426007926646,
            ),
            BeneficiaryFactory(
                first_name="Vasile",
                last_name="Troscot",
                age=80,
                phone="68078000",
                landline="22835600",
                zone="centru",
                address="str G. Asachi 56",
                entrance="5",
                floor="5",
                apartment="5",
                special_condition="deaf_mute",
                created_at="2020-01-08",
                longitude=28.845719996559724,
                latitude=47.03226007926646,
            ),
        ]
        for i in range(4):
            beneficiaries.append(
                BeneficiaryFactory(
                    first_name="Vasile {}".format(i),
                    last_name="Troscot",
                    age=80,
                    phone="6807800{}".format(i + 1),
                    landline="2283560{}".format(i + 1),
                    zone=random.choice(["centru", "botanica", "telecentru"]),
                    address="str G. Asachi 5{}".format(i + 1),
                    entrance="5",
                    floor="5",
                    apartment="5",
                    special_condition="deaf_mute",
                    created_at="2020-01-08",
                    longitude=28.812844986831664 + random.random() * 0.01,
                    latitude=47.01820503506154 + random.random() * 0.01,
                )
            )
        operator = User.objects().first()

        for idx, beneficiary in enumerate(beneficiaries):
            beneficiary.save()

            if idx <= 1:  # Only first two beneficiaries do not have requests
                continue

            cluster = ClusterFactory(volunteer=volunteers[idx % 2])
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

            # Confirmed request
            req = RequestFactory(
                beneficiary=beneficiary,
                user=operator,
                status="confirmed",
                type=random.choice(["medicine", "grocery", "warm_lunch"]),
                created_at=f"2020-04-0{idx + 1}",
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

        for idx, request in enumerate(Request.objects()):
            # New request
            notification = NotificationFactory(
                request=request, type="new_request", subject=fake.sentence(), created_at=fake.date_this_month(),
            )
            notification.save()
            # Assign new notification to user who created Request
            NotificationUser.assign_notification_to_users(self=notification, status="new")

            # Cancelled request
            notification = NotificationFactory(
                request=request, type="canceled_request", subject=fake.sentence(), created_at=fake.date_this_month(),
            )
            notification.save()
            # Assign seen notification to user who created Request
            NotificationUser.assign_notification_to_users(self=notification, status="seen")

    elif config.FLASK_ENV == "production":
        registerOperator(
            {
                "email": f"{os.environ.get('DEFAULT_USERNAME').lower()}@example.com",
                "password": os.environ.get("DEFAULT_PASSWORD"),
                "roles": ["admin"],
            },
            "admin",
        )

    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(seed_db_command)
