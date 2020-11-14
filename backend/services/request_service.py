from flask import jsonify

from models import Beneficiary, Request, Cluster

from utils import search


def requests_by_filters(filters, page=1, per_page=10):
    per_page = int(per_page)
    offset = (int(page) - 1) * per_page
    records = Request.objects()

    if filters.get("b_id"):
        beneficiary = Beneficiary.objects(id=filters.get("b_id")).get()
        records = records.filter(beneficiary=beneficiary)

    if filters.get("query"):
        query_search_fields = ["first_name", "last_name", "phone"]
        beneficiaries = search.model_keywords_search(Beneficiary, query_search_fields, filters.get("query").split())
        records = records.filter(beneficiary__in=beneficiaries)

    if filters.get("zone"):
        beneficiaries = Beneficiary.objects(zone=filters.get("zone"))
        records = records.filter(beneficiary__in=beneficiaries)

    if filters.get("created_at"):
        beneficiaries = Beneficiary.objects(created_at=filters.get("created_at"))
        records = records.filter(beneficiary__in=beneficiaries)

    if filters.get("cluster_id"):
        cluster = Cluster.objects(id=filters.get("cluster_id")).get()
        records = records.filter(cluster=cluster)

    if filters.get("status"):
        records = records.filter(status=filters.get("status"))

    if filters.get("type"):
        records = records.filter(type=filters.get("type"))

    if filters.get("id"):
        records = records.filter(id=filters.get("id"))

    count = records.count()
    reqs = []

    for record in records.order_by("-created_at").skip(offset).limit(per_page):
        entry = dict(
            _id=str(record.id),
            status=record.status,
            urgent=record.urgent,
            type=record.type,
            number=record.number,
            comments=record.comments,
            has_symptoms=record.has_symptoms,
            created_at=record.created_at,
        )
        volunteer = record.cluster and record.cluster.volunteer or None
        if volunteer:
            entry.update(
                dict(
                    volunteer=dict(
                        _id=str(volunteer.id),
                        first_name=volunteer.first_name,
                        last_name=volunteer.last_name,
                        cluster_id=str(record.cluster.id),
                    )
                )
            )
        beneficiary = record.beneficiary or None
        if beneficiary:
            entry.update(
                dict(
                    beneficiary=dict(
                        _id=str(beneficiary.id),
                        first_name=beneficiary.first_name,
                        last_name=beneficiary.last_name,
                        latitude=beneficiary.latitude,
                        longitude=beneficiary.longitude,
                        zone=beneficiary.zone,
                    )
                )
            )

        reqs.append(entry)

    return jsonify({"list": reqs, "count": count})
