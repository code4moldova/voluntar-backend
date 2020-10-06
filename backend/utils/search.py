from mongoengine.queryset.visitor import Q
from flask import jsonify


def model_keywords_search(model, search_fields, search_words_list, search_result=None):
    try:
        if len(search_words_list) == 0:
            return search_result

        db_query = None
        for field in search_fields:
            q = Q(**{"%s__istartswith" % field: search_words_list[0]})
            if db_query:
                db_query = db_query | q
            else:
                db_query = q

        if search_result is None:
            search_result = model.objects(db_query)
        else:
            search_result = search_result.filter(db_query)

        search_words_list.pop(0)
        return model_keywords_search(model, search_fields, search_words_list, search_result)
    except Exception as error:
        return jsonify({"error": str(error)}), 400
