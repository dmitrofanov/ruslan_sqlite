from glob import glob
from pathlib import Path
import csv


TYPES_TO_VALUES = {
	'int': lambda x: x,
	'str': lambda x: f"'{x}'",
	'date': lambda x: f"'{x}'",
	'float': lambda x: x,
	'bool': lambda x: x.upper(),
}

TYPES_TO_DATATYPES = {
	'int': 'INTEGER',
	'str': 'TEXT',
	'date': 'TEXT',
	'float': 'REAL',
	'bool': 'INTEGER',
}

def concat_body_line(line, types):
	result = []
	for i, type in enumerate(types):
		value = line[i]
		result.append(TYPES_TO_VALUES[type](value))
	return ', '.join(result)

def prepare_create_table(table_name, names, types):
	table_template = "CREATE TABLE {} ({});"
	columns_template = " {} {}"
	columns = ",".join(columns_template.format(n, t) for n, t in zip(names, types))
	return table_template.format(table_name, columns)


def write_table_data(table_name, header, body, fp):
	fp.write('\n')
	header_names = [[col for col in h.split(':')][0] for h in header]
	header_types = [[col for col in h.split(':')][1] for h in header]
	fp.write(prepare_create_table(table_name, header_names, header_types))
	fp.write('\n')
	template = 'INSERT INTO {} ({}) VALUES ({});'
	for line in body:
		fp.write(
			template.format(
				table_name,
				', '.join(header_names),
				concat_body_line(line, header_types)
			)
		)
		fp.write('\n')
	fp.write('\n')


with open('inserts.sql', 'w', encoding='UTF-8') as out:
	for filename in glob('*.csv'):
		file = Path(filename)
		with file.open(encoding='UTF-8') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='"')
			lines = list(reader)
			header, *body = lines
			write_table_data(file.stem, header, body, out)