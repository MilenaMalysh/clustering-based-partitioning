"""CREATE TABLE LINEITEM (
L_ORDERKEY INTEGER NOT NULL,
L_PARTKEY INTEGER NOT NULL,
L_SUPPKEY INTEGER NOT NULL,
L_LINENUMBER INTEGER NOT NULL,
L_QUANTITY DECIMAL(15,2) NOT NULL,
L_EXTENDEDPRICE DECIMAL(15,2) NOT NULL,
L_DISCOUNT DECIMAL(15,2) NOT NULL,
L_TAX DECIMAL(15,2) NOT NULL,
L_RETURNFLAG CHAR(1) NOT NULL,
L_LINESTATUS CHAR(1) NOT NULL,
L_SHIPDATE DATE NOT NULL,
L_COMMITDATE DATE NOT NULL,
L_RECEIPTDATE DATE NOT NULL,
L_SHIPINSTRUCT CHAR(25) NOT NULL,
L_SHIPMODE CHAR(10) NOT NULL,
L_COMMENT VARCHAR(44) NOT NULL);
"""

from input_data.temp_input_data import table_name


def copy_table_structure(connector, table_copy_name):
    connector.query("CREATE TABLE {0} ( like {1} including all)".format(table_copy_name, table_name))
    connector.commit()


def copy_table_data(connector, table_copy_name):
    connector.query("INSERT INTO {0} SELECT * FROM {1};".format(table_copy_name, table_name))
    connector.commit()


def add_column(connector, column_name):
    connector.query("ALTER TABLE {0} ADD COLUMN {1} INTEGER;".format(table_name, column_name))
    connector.commit()


def drop_column(connector, column_name):
    connector.query("ALTER TABLE {0} DROP COLUMN {1};".format(table_name, column_name))
    connector.commit()


def drop_table(connector, table_to_delete):
    connector.query("DROP TABLE {0} CASCADE;".format(table_to_delete))
    connector.commit()


def insert_data_from_table(connector, target_table, src_table, where_clause=None):
    connector.query(("INSERT INTO {0} SELECT * FROM {1}" + (" WHERE {2};" if where_clause else ";"))
                    .format(target_table, src_table, where_clause))
    connector.commit()


def create_table(connector, table_to_create, check_condition, inherits_from):
    connector.query(("CREATE TABLE {0}" + " (CHECK ({1})) INHERITS ({2});" if inherits_from else ';').format(
        table_to_create, check_condition, inherits_from))
    connector.commit()


def create_insertion_rule(connector, table_to_create, check_condition, inherits_from):
    connector.query(
        "CREATE RULE insert_{0} AS ON INSERT TO {1} WHERE ({2}) DO INSTEAD INSERT INTO {0} VALUES (NEW.*);".format(
            table_to_create, inherits_from, check_condition))
    connector.commit()


def drop_insertion_rule(connector, subtable_name, master_table):
    connector.query(
        "DROP RULE insert_{0} ON {1} CASCADE".format(
            subtable_name, master_table))
    connector.commit()