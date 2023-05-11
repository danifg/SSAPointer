
for DATASET in ds_unis mpqa ca eu norec; do

    for SPLIT in dev test train; do
	for MODE in head_final head_first; do
	    python ./scripts/convert.py ./data_conll/"$DATASET"_"$MODE"_"$SPLIT".conll ./data_dag/"$DATASET"_"$MODE"_"$SPLIT".dag
	done;
    done;
done;
