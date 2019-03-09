from input_data.temp_input_data import table_name


def select_count(connector, where_clauses):
    return connector.query(
        "SELECT COUNT(*) FROM {0} WHERE {1};".format(table_name, ' AND '.join(where_clauses))
    ).fetchone()[0]
