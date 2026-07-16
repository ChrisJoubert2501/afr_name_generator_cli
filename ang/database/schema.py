import schema

from ang import NAME_GENDERS

name_entry_schema = schema.Schema(
    {
        "name": schema.And(str, len),
        "prevalence": schema.And(schema.Use(int), lambda n: 1 <= n <= 10),
        "gender": schema.And(str, lambda gender: gender in NAME_GENDERS),
    }
)

surname_entry_schema = schema.Schema(
    {
        "surname": schema.And(str, len),
        "prevalence": schema.And(schema.Use(int), lambda n: 1 <= n <= 10),
    }
)

ang_database_schema = schema.Schema(
    {
        "names": [name_entry_schema],
        "surnames": [surname_entry_schema],
    }
)
