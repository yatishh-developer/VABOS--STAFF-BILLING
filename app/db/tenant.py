from sqlalchemy import Select


def tenant_filter(query: Select, model: type, *, business_id: str, branch_id: str | None = None) -> Select:
    """Apply mandatory tenant filters for authenticated staff routes."""
    query = query.where(model.business_id == business_id)
    if branch_id is not None and hasattr(model, 'branch_id'):
        query = query.where(model.branch_id == branch_id)
    return query
