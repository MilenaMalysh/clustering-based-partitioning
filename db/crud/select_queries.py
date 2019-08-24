from input_data.temp_input_data import table_name


def select_count(connector, where_clauses):
    return connector.query(
        "SELECT COUNT(*) FROM {0} WHERE {1};".format(table_name, ' AND '.join(where_clauses))
    ).fetchone()[0]


def select_ordered_values(connector, column):
    return connector.query(
        "SELECT {0} FROM {1} ORDER BY {0};".format(column, table_name)
    ).fetchall()


def select_all(connector, table):
    return connector.query(
        "SELECT * FROM {0};".format(table)
    ).fetchall()


def select_column_type(connector, column):
    return connector.query(
        "SELECT data_type FROM information_schema.columns WHERE table_name = '{0}' AND column_name = '{1}';".format(
            table_name, column)
    ).fetchone()[0]
