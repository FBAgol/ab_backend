from sqlalchemy.inspection import inspect

def to_dict(obj):
    """
    Diese Funktion wandelt ein SQLAlchemy-Objekt in ein Dictionary um,
    ohne dass Zirkularitätsprobleme auftreten.
    """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
