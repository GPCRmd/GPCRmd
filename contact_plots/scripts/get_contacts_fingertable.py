import os

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

def prepare_tables(original_table, new_table, itype, table_summary, firstline_summary):
	"""
	Adds a reverse-residue version of the interaction for each interaction (row) in the table. Also adds a column with the itype code
	Deltes original table at the end. 
	Also writes everything to a summary table
	"""

	#Duplicate lines by writing reciprocal contacts
	table_file_provi = open(table_output_provi, "r")
	table_file = open(table_output, "w")
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
			if firstline_summary: 
				table_summary.write(line_joined)
				firstline_summary = False

		#For rest of lines: print the interaction and also the reverse-residue version of this interaction
		else:
			line_tab.append(str(itype + "\n"))
			line_regular = "\t".join(line_tab)
			line_tab[0], line_tab[1] = line_tab[1], line_tab[0]
			line_reverse = "\t".join(line_tab)
			table_file.write(line_regular)
			table_file.write(line_reverse)
			table_summary.write(line_regular)
			table_summary.write(line_reverse)

	table_file_provi.close()
	table_file.close()

	os.remove(str("%scontact_tables/compare_%s_provi.tsv" % (files_path, itype)))


# Set paths
get_contacts_path="/protwis/sites/protwis/contact_plots/scripts/get_contacts/"
scripts_path="/protwis/sites/protwis/contact_plots/scripts/"
files_path="/protwis/sites/files/Precomputed/get_contacts_files/"

# Creating folder, if it doesn't exist
mkdir_p(str(files_path + "contact_tables"))

#Get dynlist
dyncsv_path = files_path + "dyn_list.csv"
dyncsv_file = open(dyncsv_path, "r")
dynlist = dyncsv_file.readline().split(",")
dyntsv = "\t".join(dynlist)
dyncsv_file.close()

#Preparing table summary
firstline_summary = True
table_summary = open(str("%scontact_tables/compare_%s.tsv" % (files_path, "summary")), "w")

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
		infreqs += str(" %sdynamic_symlinks/%s/frequency_tables/%s-0_freqs_%s.tsv" % (files_path, dynid, dynid, itype));
		#TODO: do something with multi-trajectory submissions

	#Getting fingerprint info by type
	table_output_provi = str("%scontact_tables/compare_%s_provi.tsv" % (files_path, itype))
	table_output = str("%scontact_tables/compare_%s.tsv" % (files_path, itype))
	os.system(str("python %sget_contact_fingerprints.py \
				--input_frequencies %s \
	            --frequency_cutoff 0.01 \
	            --column_headers %s \
	            --table_output %s") % (get_contacts_path, infreqs, dyntsv, table_output_provi))

	#Modifying tables to prepare them for table-to-dataframe script
	print("Preparing summary table")
	prepare_tables(table_output_provi, table_output, itype, table_summary, firstline_summary)

	#Only a header is needed for summary
	firstline_summary = False

table_summary.close()

# Activate table_to_dataframe
for itype in itypes:
	for ipartner in ipartners:
		if (itype in nolg_itypes) and (ipartner == "lg"):
			continue
		if (itype in noprt_itypes) and (ipartner == "prt"):
			continue

		print("processing %s and %s dataframes" % (itype, ipartner))
		os.system("python %stable_to_dataframe.py %s %s" % (scripts_path, itype, ipartner))