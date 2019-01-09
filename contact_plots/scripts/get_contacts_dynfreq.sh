# Set paths
get_contacts_path="/protwis/sites/protwis/contact_plots/scripts/get_contacts/"
scripts_path="/protwis/sites/protwis/contact_plots/scripts/"
files_basepath="/protwis/sites/files/Precomputed/get_contacts_files/"
files_path="/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/"$5"/"

# Set folder
mkdir -p /protwis/sites/files/Precomputed/get_contacts_files

#Initial files and data
topologyfile=$1
trajectoryfile=$2
dictfile=$3
ligandfile=$4
dynname=$5 #Ex: dyn1

#Water bridges and Hydrogen bonds types
hb="hbbb hbsb hbss hbls hblb" # A general category for HB is required
wb='wb lwb' # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
wb2='wb2 lwb2'

#Extracting ligand information
echo "ligand things"
ligand_sel=`awk 'NR==1{ printf "(resname %s and resid %s)",$3,$1 } NR>1{ printf " or (resname %s and resid %s) ",$3,$1 }' $ligandfile`;

#Precalculating labelfile
echo "computing labelfile"
python ${scripts_path}create_labelfile.py $dictfile $dynname $files_path $ligandfile

#Getting dynamic contacts
echo "computing dynamic contacts"
python ${get_contacts_path}get_dynamic_contacts.py         \
        --topology $topologyfile  \
        --trajectory $trajectoryfile       \
        --sele "protein or $ligand_sel"  \
        --itypes all    \
        --ligand "$ligand_sel" \
        --output ${files_path}${dynname}_dynamic.tsv

#Adding new dynname to list of dynnames if doesnt already exists, and getting dynlist
echo "reading dyn lists"
dyn_csv=${files_basepath}dyn_list.csv
[ -e $dyn_csv ] || echo -n $dynname > $dyn_csv
grep "$dynname" $dyn_csv || echo -n ",$dynname" >> $dyn_csv
dynlist=`cat $dyn_csv`
dyntsv=${dynlist//,/ }

# Compute frequencies and fingerprint by itype
mkdir -p ${files_path}frequency_tables
# For regular types
for inter in sb hp pc ps ts vdw hbbb hbsb hbss hbls hblb all;
do {

	#Getting frequencies
	echo "computing $inter frequencies"
	python ${get_contacts_path}get_contact_frequencies.py \
			--input_files ${files_path}${dynname}_dynamic.tsv \
			--itypes $inter \
			--label_file ${files_path}${dynname}_labels.tsv \
			--output ${files_path}frequency_tables/${dynname}_freqs_${inter}.tsv

	# Filter ligand interactions if itype is one of the interaction types unable to deal correctly with ligands
	if [ $inter == "sb" ] || [ $inter == "pc" ] || [ $inter == "ts" ] || [ $inter == "ps" ] || [ $inter == "hp" ]; then
	        sed -i '/Ligand/d' ${files_path}frequency_tables/*_freqs_${inter}.tsv;
	fi;


}; done;

# For wb, wb2 and hb (this mess will be repaired when passing to python)
echo "computing $wb frequencies"
python ${get_contacts_path}get_contact_frequencies.py \
		--input_files ${files_path}${dynname}_dynamic.tsv \
		--itypes $wb \
		--label_file ${files_path}${dynname}_labels.tsv \
		--output ${files_path}frequency_tables/${dynname}_freqs_wb.tsv

echo "computing $wb2 frequencies"
python ${get_contacts_path}get_contact_frequencies.py \
		--input_files ${files_path}${dynname}_dynamic.tsv \
		--itypes $wb2 \
		--label_file ${files_path}${dynname}_labels.tsv \
		--output ${files_path}frequency_tables/${dynname}_freqs_wb2.tsv

echo "computing $hb frequencies"
python ${get_contacts_path}get_contact_frequencies.py \
		--input_files ${files_path}${dynname}_dynamic.tsv \
		--itypes $hb \
		--label_file ${files_path}${dynname}_labels.tsv \
		--output ${files_path}frequency_tables/${dynname}_freqs_hb.tsv
