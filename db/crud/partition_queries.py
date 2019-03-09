from input_data.temp_input_data import table_name


def create_partition(connector):
    connector.query("SELECT " + table_name + "('hypo_part_range', 'PARTITION BY RANGE(id)');")

# TODO: remove created hypothetical partition