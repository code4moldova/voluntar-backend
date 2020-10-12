from flask import jsonify

from models import Beneficiary, Request


def requests_by_filters(filters, page=1, per_page=10):
    per_page = int(per_page)
    offset = (int(page) - 1) * per_page
    records = Request.objects()

    if filters.get("b_id"):
        beneficiary = Beneficiary.objects(id=filters.get("b_id")).get()
        records = records.filter(beneficiary=beneficiary)

    count = records.count()
    reqs = []

    for record in records.order_by("-created_at").skip(offset).limit(per_page):
        entry = dict(
            _id=str(record.id),
            status=record.status,
            urgent=record.urgent,
            comments=record.comments,
            has_symptoms=record.has_symptoms,
            created_at=record.created_at,
        )
        volunteer = record.cluster and record.cluster.volunteer or None
        if volunteer:
            entry.update(
                dict(
                    volunteer=dict(
                        _id=str(volunteer.id), first_name=volunteer.first_name, last_name=volunteer.last_name,
                    )
                )
            )

        reqs.append(entry)

    return jsonify({"list": reqs, "count": count})
