for DATASET in ds_unis mpqa ca eu norec; do

    for SPLIT in dev test train; do
	for MODE in head_final head_first; do
	    ./scripts/conllu_to_conllx.pl ./data_ssa/"$DATASET"/"$MODE"/"$SPLIT".conllu > ./data_conll/"$DATASET"_"$MODE"_"$SPLIT".conll
	done;
    done;
done;
