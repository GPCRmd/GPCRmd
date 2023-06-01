import os
from django.conf import settings


def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

def prepare_tables(original_table, new_table, itype):
	"""
	Adds a column with the itype code, and modifies header slightly
	"""

	#Duplicate lines by writing reciprocal contacts
	table_file_provi = open(original_table, "r")
	table_file = open(new_table, "w")
	first_line = True
	for line in table_file_provi:

		line = line.rstrip()
		line_tab = line.split("\t")

		#For headers: Print header, appending the Position1 Posidtion2 and itype headers
		if first_line:
			line_tab[0], line_tab[1] = "Position1", "Position2"
			line_tab.append("itype\n")
			line_joined = "\t".join(line_tab)
			table_file.write(line_joined)
			first_line = False

		#For rest of lines: print the interaction and also the reverse-residue version of this interaction
		else:
			line_tab.append(str(itype + "\n"))
			line_regular = "\t".join(line_tab)
			table_file.write(line_regular)

	os.remove(original_table)
	table_file_provi.close()
	table_file.close()

# Set paths
get_contacts_path="~/bin/"
scripts_path=settings.MODULES_ROOT + "/contact_maps/scripts/"
files_path=settings.MEDIA_ROOT + "Precomputed/get_contacts_files/"

# Creating folder, if it doesn't exist
mkdir_p(str(files_path + "contact_tables"))

#Get dynlist
dyncsv_path = files_path + "dyn_list.csv"
with open(dyncsv_path, "r") as dyncsv_file:
	dynlist = dyncsv_file.readline().replace('\n','').split(",")
	dyntsv = "\t".join(dynlist)

#itype sets
itypes = set(("wb", "wb2", "sb","hp","pc","ps","ts","vdw", "hb", "hbbb","hbsb","hbss","hbls","hblb","all"))
nolg_itypes = set(("sb","pc","ts","ps","hbbb","hbsb","hbss","hp"))
noprt_itypes = set(("hbls","hblb"))
ipartners = set(("lg","prt","prt_lg"))

#Get fingerprint table by interaction type (itype)
for itype in itypes:

	#Creating list of frequency files for calculating fingerprint
	infreqs = ""
	for dynid in dynlist:
		if not dynid:
			continue
		infreqs += str(" %sdynamic_symlinks/%s/frequency_tables/%s_freqs_%s.tsv" % (files_path, dynid, dynid, itype));
		#TODO: do something with multi-trajectory submissions

	#Getting fingerprint info by type
	table_output_provi = str("%scontact_tables/compare_%s_provi.tsv" % (files_path, itype))
	os.system(str("/opt/gpcrmdenv/bin/activate;python %sget_contact_fingerprints.py \
				--input_frequencies %s \
	            --frequency_cutoff 0.00 \
	            --column_headers %s \
	            --table_output %s") % (get_contacts_path, infreqs, dyntsv, table_output_provi))

	#Modifying tables to prepare them for table-to-dataframe script
	table_output = str("%scontact_tables/compare_%s.tsv" % (files_path, itype))
	prepare_tables(table_output_provi, table_output, itype)

# Activate table_to_dataframe
os.system("/opt/gpcrmdenv/bin/activate;python %stable_to_dataframe.py --all" % (scripts_path))