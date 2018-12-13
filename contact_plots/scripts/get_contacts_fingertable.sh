# Set paths
get_contacts_path="/protwis/sites/protwis/contact_plots/scripts/get_contacts/"
scripts_path="/protwis/sites/protwis/contact_plots/scripts/"
files_path="/protwis/sites/files/Precomputed/get_contacts_files/"

#Get dynlist
dynlist=`cat ${files_path}dyn_list.csv`
dyntsv=${dynlist//,/ }

for inter in wb wb2 sb hp pc ps ts vdw hb hbbb hbsb hbss hbls hblb all;
do {
	#Creating list of frequency files for calculating fingerprint
	infreqs=""
	for dynid in $dyntsv;
	do {
		infreqs="$infreqs ${files_path}dynamic_symlinks/${dynid}/frequency_tables/${dynid}_freqs_${inter}.tsv";
	}; 
	done;

	#Getting fingerprint info by type
	python ${get_contacts_path}get_contact_fingerprints.py \
			--input_frequencies $infreqs \
            --frequency_cutoff 0.00 \
            --column_headers $dyntsv\
            --cluster_columns True\
            --table_output ${files_path}contact_tables/compare_${inter}_provi.tsv 

	# Duplicate contact files, writing reciprocal contacts to file
	awk ' NR==1 {print "END";} $0=="END"{exit} NR>1 {OFS="\t"; t = $1; $1 = $2; $2 = t; print; } ' ${files_path}contact_tables/compare_${inter}_provi.tsv >> ${files_path}contact_tables/compare_${inter}_provi.tsv
	sed -i '/END/d'  ${files_path}contact_tables/compare_${inter}_provi.tsv

	# Add a column with the interaction type
	awk 'NR==1 { OFS="\t"; print($0,"itype"); } NR>1 { OFS="\t"; print $0,"'$inter'" }' ${files_path}contact_tables/compare_${inter}_provi.tsv > ${files_path}contact_tables/compare_${inter}.tsv 
	rm ${files_path}contact_tables/compare_${inter}_provi.tsv

}; done;

# Merge toghether in one file, deleting all headers except first and adding Position to headers
cat ${files_path}contact_tables/* > ${files_path}contact_tables/compare_summary.tsv
sed -i '1!{/itype/d;}' ${files_path}contact_tables/compare_summary.tsv
sed -i '1s/^/Position1    Position2/' ${files_path}contact_tables/compare_summary.tsv

# Activate table_to_dataframe to recompute
for inter in wb wb2 sb hp pc ps ts vdw hb hbbb hbsb hbss hbls hblb all;
do {
	for ligandonly in lg lg_prt prt;
	do {
		if ([ $inter == "sb" ] || [ $inter == "hp" ] || [ $inter == "pc" ] || [ $inter == "hbbb" ] || [ $inter == "hbsb" ] || [ $inter == "hbss" ] || [ $inter == "ts" ] || [ $inter == "ps" ]) && [ $ligandonly == "lg" ] ; then
			continue
		fi;
		if ([ $inter == "hblb" ] || [ $inter == "hbls" ]) && [ $ligandonly == "prt" ] ; then
			continue
		fi;
		echo "processing $inter and $ligandonly dataframes"
		python ${scripts_path}table_to_dataframe.py $inter $ligandonly;
	}
	done;
	}
done;