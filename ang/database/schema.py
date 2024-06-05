import schema

name_entry_schema = schema.Schema(
    {
        "name": schema.And(str, len),
        "prevalence": schema.And(schema.Use(int), lambda n: 1 <= n <= 10),
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
