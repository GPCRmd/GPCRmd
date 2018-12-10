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

#Extracting ligand information
echo "ligand things"
ligand_sel=`awk '{ printf "or (resname %s and resid %s) ",$3,$1 }' $ligandfile`;

#Precalculating labelfile
echo "computing labelfile"
python ${scripts_path}create_labelfile.py $dictfile $dynname $files_path $ligandfile

#Getting dynamic contacts
echo "computing dynamic contacts"
python ${get_contacts_path}get_dynamic_contacts.py         \
        --topology $topologyfile  \
        --trajectory $trajectoryfile       \
        --sele "protein $ligand_sel"  \
        --itypes all    \
        --ligand "resname $ligres and resid $lignum" \
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
for inter in wb lwb wb2 lwb2 sb hb pc ps ts vdw hbbb hbsb hbss hbls hblb all;
do {

	#Getting frequencies
	echo "computing frequencies"
	mkdir -p frequency_tables
	python ${get_contacts_path}get_contact_frequencies.py \
			--input_files ${files_path}${dynname}_dynamic.tsv \
			--itypes $inter \
			--label_file ${files_path}${dynname}_labels.tsv \
			--output ${files_path}frequency_tables/${dynname}_freqs_${inter}.tsv

}; done;
