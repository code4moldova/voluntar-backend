from bson import ObjectId

from models import Beneficiary, Tags


class BeneficiaryList:
    # TODO add all fields
    # nume, prenume, varsta, regiune/raion, strada, offer, urgenta,
    # are bani, are dizabilitati, are curator, pranz cald, produse alimentare,
    # medicamente, plata cu cardul, comentarii
    FIELD_TITLE = {
        "last_name": "Nume",
        "first_name": "Prenume",
        "age": "Vîrsta",
        "have_money": "Are bani?",
    }
    FIELDS = "last_name first_name age have_money".split()
    FIELDS += [
        "phone",
        "address",
        "zone_address",
        "offer",
        "comments",
        "urgent",
        "curator",
        "has_disabilities",
        "black_list",
    ]
    tag2v = {"offer": "offer", "age": "age", "zone_address": "sector"}

    def run(self):
        headers = [self.FIELD_TITLE[f] if f in self.FIELD_TITLE else f for f in self.FIELDS]
        rows = [headers]

        for user in Beneficiary.objects().order_by("+last_name", "+first_name", "-age"):
            row = []
            for field in self.FIELDS:
                value = getattr(user, field)
                if field in self.tag2v.keys():
                    if ObjectId.is_valid(value):
                        row.append(value)
                    else:
                        row.append(value)
                elif isinstance(value, bool):
                    row.append(1 if value else 0)
                else:
                    row.append(value)
            rows.append(row)

        return rows


SERVICES = {
    "beneficiaries": BeneficiaryList,
}


def service(slug):
    return SERVICES[slug]().run()
