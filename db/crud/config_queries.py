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
    connector.query("CREATE TABLE {0} ( like {1} including all)".format(table_name, table_copy_name))
    connector.commit()


def add_column(connector, column_name):
    connector.query("ALTER TABLE {0} ADD COLUMN {1} INTEGER;".format(table_name, column_name))
    connector.commit()


def drop_column(connector, column_name):
    connector.query("ALTER TABLE {0} DROP COLUMN {1};".format(table_name, column_name))
    connector.commit()
