"""Term groups shared across matching/suggestion/scoring modules.

Kept in one place so a technology's group membership (e.g. which items count
as "SQL basics") is defined once instead of drifting across files.
"""

SQL_TERMS = {"SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE"}

GIT_TERMS = {"Git", "branches", "pull requests", "code review"}

BRAZILIAN_CITIES = (
    "Manaus",
    "Recife",
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Porto Alegre",
    "Brasília",
    "Fortaleza",
    "Salvador",
)
