#Initial files and data
topologyfile=$1
trajectoryfile=$2
dictfile=$3
ligandfile=$4
dynname=$5 #Ex: dyn1

#Extracting ligand information
echo "ligand things"
lignum=`awk '{print $1}' $ligandfile`;
ligchain=`awk '{print $2}' $ligandfile`;
ligres=`awk '{print $3}' $ligandfile`;

#Precalculating labelfile
echo "computing labelfile"
python create_labelfile.py $dictfile $dynname $ligandfile

#Getting dynamic contacts
echo "computing dynamic contacts"
#get_dynamic_contacts.py         \
#        --topology $topologyfile  \
#        --trajectory $trajectoryfile       \
#        --sele "protein or (resname $ligres and resid $lignum)"  \
#        --itypes all    \
#        --ligand "resname $ligres and resid $lignum" \
#        --output ${dynname}_dynamic.tsv


#Adding new dynname to list of dynnames if doesnt already exists, and getting dynlist
echo "reading dyn lists"
[ -e dyn_list.csv ] || echo -n $dynname > dyn_list.csv
grep "$dynname" dyn_list.csv || echo -n ",$dynname" >> dyn_list.csv
dynlist=`cat dyn_list.csv`
dyntsv=${dynlist//,/ }

# Compute frequencies and fingerprint by itype
mkdir -p contact_tables
for inter in wb lwb wb2 lwb2 sb hb pc ps ts vdw hbbb hbsb hbss hbls hblb all;
do {

	#Getting frequencies
	echo "computing frequencies"
	mkdir -p frequency_tables
	get_contact_frequencies.py \
			--input_files ${dynname}_dynamic.tsv \
			--itypes $inter \
			--label_file ${dynname}_labels.tsv \
			--output frequency_tables/${dynname}_freqs_${inter}.tsv

	#Only calculate fingerprint if more than a simulation is charged
	if [[ $dynlist == *","*  ]]; then
		#Creating list of frequency files for calculating fingerprint
		infreqs=""
		for dynid in $dyntsv;
		do {
			infreqs="$infreqs frequency_tables/${dynid}_freqs_${inter}.tsv";
		}; 
		done;
		#Getting fingerprint info by type
		get_contact_fingerprints.py \
				--input_frequencies $infreqs \
	            --frequency_cutoff 0.00 \
	            --column_headers $dyntsv\
	            --cluster_columns True\
	            --table_output contact_tables/compare_${inter}_provi.tsv 

		# Filter ligand interactions if itype is one of the interaction type unable to deal correctly with ligands
		if [ $inter == "sb" ] || [ $inter == "pc" ] || [ $inter == "ts" ] || [ $inter == "ps" ]; then
		        sed '/Ligand/d' frequency_tables/*_freqs_${inter}.tsv;
		fi;

		# Duplicate contact files, writing reciprocal contacts to file
		awk ' NR>1 {OFS="\t"; t = $1; $1 = $2; $2 = t; print; } ' contact_tables/compare_${inter}_provi.tsv >> contact_tables/compare_${inter}_provi.tsv

		# Add a column with the interaction type
		awk 'NR==1 { OFS="\t"; print($0,"itype"); } NR>1 { OFS="\t"; print $0,"'$inter'" }' contact_tables/compare_${inter}_provi.tsv > contact_tables/compare_${inter}.tsv 
		rm contact_tables/compare_${inter}_provi.tsv

	fi;
}; done;

# Merge toghether in one file, deleting all headers except first and adding Position to headers
cat contact_tables/* > contact_tables/compare_summary.tsv
sed -i '1!{/itype/d;}' contact_tables/compare_summary.tsv
sed -i '1s/^/Position1    Position2/' contact_tables/compare_summary.tsv 