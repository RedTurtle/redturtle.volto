# -*- coding: utf-8 -*-
CUSTOM = {
    "allowedRolesAndUsers": 80,
    "effectiveRange": 100,
}


def rank_index(index, query):
    if (
        index == "UID"
        and isinstance(query.get("UID"), dict)  # noqa
        and query["UID"].get("not")  # noqa
    ):
        return 100
    return CUSTOM.get(index, 0)


def Catalog_sorted_search_indexes(self, query):
    return sorted(
        self._orig_sorted_search_indexes(query), key=lambda i: (rank_index(i, query), i)
    )
