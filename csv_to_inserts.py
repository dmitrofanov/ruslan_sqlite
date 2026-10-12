from glob import glob
from pathlib import Path
import csv
	

def concat_body_line(line, types):
	result = []
	for i, type in enumerate(types):
		if type == 'int':
			result.append(line[i])
		elif type == 'str':
			result.append(f"'{line[i]}'")
		elif type == 'date':
			result.append(f"'{line[i]}'")
	return ','.join(result)


def write_table_data(table_name, header, body, fp):
	fp.write('\n')
	header_names = [[col for col in h.split(':')][0] for h in header]
	header_types = [[col for col in h.split(':')][1] for h in header]
	template = 'INSERT INTO {} ({}) VALUES ({});'
	for line in body:
		fp.write(
			template.format(
				table_name,
				','.join(header_names),
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