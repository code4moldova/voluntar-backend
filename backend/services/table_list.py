from bson import ObjectId

from models import Beneficiary, Volunteer, Request


class BeneficiaryList:
    FIELD_TITLE = {}
    FIELDS = "last_name first_name age phone landline zone address apartment entrance floor black_list created_at created_by special_condition latitude longitude".split()

    def run(self):
        headers = [self.FIELD_TITLE[f] if f in self.FIELD_TITLE else f for f in self.FIELDS]
        rows = [headers]

        for user in Beneficiary.objects().order_by("+last_name", "+first_name", "-age"):
            row = []
            for field in self.FIELDS:
                value = getattr(user, field)
                if isinstance(value, bool):
                    row.append(1 if value else 0)
                else:
                    row.append(value)
            rows.append(row)

        return rows


class VolunteerList:
    FIELD_TITLE = {}
    FIELDS = "last_name first_name age phone zone address email facebook_profile role availability_hours_start availability_hours_end availability_days status created_at created_by".split()

    def run(self):
        headers = [self.FIELD_TITLE[f] if f in self.FIELD_TITLE else f for f in self.FIELDS]
        rows = [headers]

        for user in Volunteer.objects().order_by("+last_name", "+first_name", "-age"):
            row = []
            for field in self.FIELDS:
                value = getattr(user, field)
                if isinstance(value, bool):
                    row.append(1 if value else 0)
                else:
                    row.append(value)
            rows.append(row)

        return rows


class RequestList:
    FIELD_TITLE = {}
    FIELDS_BENEFICIARY = (
        "last_name first_name age phone landline zone address apartment entrance floor longitude latitude".split()
    )
    FIELDS_VOLUNTEER = "last_name first_name age phone".split()
    FIELDS = "type status has_symptoms comments".split()

    def run(self):
        headers = (
            ["beneficiary_" + i for i in self.FIELDS_BENEFICIARY]
            + self.FIELDS
            + ["volunteer_" + i for i in self.FIELDS_VOLUNTEER]
        )
        rows = [headers]

        for request in Request.objects().order_by("+last_name", "+first_name", "-age"):
            row = []
            for field in self.FIELDS_BENEFICIARY:
                value = getattr(request.beneficiary, field)
                if isinstance(value, bool):
                    row.append(1 if value else 0)
                else:
                    row.append(value)
            for field in self.FIELDS:
                value = getattr(request, field)
                if isinstance(value, bool):
                    row.append(1 if value else 0)
                else:
                    row.append(value)
            for field in self.FIELDS_VOLUNTEER:
                value = ""
                if request.cluster:
                    value = getattr(request.cluster.volunteer, field)
                if isinstance(value, bool):
                    row.append(1 if value else 0)
                else:
                    row.append(value)
            rows.append(row)

        return rows


SERVICES = {
    "beneficiaries": BeneficiaryList,
    "volunteers": VolunteerList,
    "requests": RequestList,
}


def service(slug):
    return SERVICES[slug]().run()
