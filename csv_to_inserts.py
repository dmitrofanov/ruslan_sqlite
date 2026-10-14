from glob import glob
from pathlib import Path
import csv


SQLITE_VALUES = {
	'int': lambda x: x,
	'str': lambda x: f"'{x}'",
	'date': lambda x: f"'{x}'",
	'float': lambda x: x,
	'bool': lambda x: x.upper(),
}

SQLITE_DATATYPES = {
	'int': 'INTEGER',
	'str': 'TEXT',
	'date': 'TEXT',
	'float': 'REAL',
	'bool': 'INTEGER',
}

CLICKHOUSE_VALUES = {
	'int': lambda x: x,
	'str': lambda x: f"'{x}'",
	'date': lambda x: f"'{x}'",
	'float': lambda x: x,
	'bool': lambda x: x.upper(),
}

CLICKHOUSE_DATATYPES = {
	'int': 'UInt64',
	'str': 'String',
	'date': 'Date',
	'float': 'Decimal',
	'bool': 'Bool',
}

DB_ENGINES ={
	'sqlite': {
		'table_template': "CREATE TABLE {} ({});",
		'values': SQLITE_VALUES,
		'datatypes': SQLITE_DATATYPES,
	},
	'clickhouse': {
		'table_template': "CREATE TABLE {} ({}) ENGINE = MergeTree();",
		'values': CLICKHOUSE_VALUES,
		'datatypes': CLICKHOUSE_DATATYPES,
	}
}

def concat_body_line(engine, line, types):
	result = []
	for i, type in enumerate(types):
		value = line[i]
		result.append(DB_ENGINES[engine]['values'][type](value))
	return "("+', '.join(result)+")"

def prepare_create_table(engine, table_name, names, types):
	columns_template = " {} {}"
	db_types = [DB_ENGINES[engine]['datatypes'][type] for type in types]
	columns = ",".join(columns_template.format(n, t) for n, t in zip(names, db_types)).strip()
	return DB_ENGINES[engine]['table_template'].format(table_name, columns)


def write_table_data(engine, table_name, header, body, fp):
	fp.write('\n')
	header_names = [[col for col in h.split(':')][0] for h in header]
	header_types = [[col for col in h.split(':')][1] for h in header]
	fp.write(prepare_create_table(engine, table_name, header_names, header_types))
	fp.write('\n')
	template = 'INSERT INTO {} ({}) VALUES\n{};'
	values = ", \n".join(concat_body_line(engine, line, header_types) for line in body)
	fp.write(
		template.format(
			table_name,
			', '.join(header_names),
			values,
		)
	)
	fp.write('\n')


with open('inserts.sql', 'w', encoding='UTF-8') as out:
	for filename in glob('*.csv'):
		file = Path(filename)
		with file.open(encoding='UTF-8') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='"')
			lines = list(reader)
			header, *body = lines
			write_table_data('clickhouse', file.stem, header, body, out)