
cp ./models/$2/*pred_test$3 ./results/best_pred_test_$2.dag


python ./scripts/gold_order_sents_conll.py ./results/best_pred_test_$2.dag ../scripts/aux/$1-GOLD-ORDER-TEST > ./results/best_pred_test_$2.dag.ordered

python ./scripts/deconvert.py ./results/best_pred_test_$2.dag.ordered ./results/best_pred_test_$2.conll.ordered

paste ./results/best_pred_test_$2.conll.ordered ../scripts/aux/$1-GOLD-WORDS-TEST > ./results/aux
cat ./results/aux | awk  '{print $1 "\t" $12 "\t" $3 "\t" $4 "\t" $5 "\t" $6 "\t" $7 "\t" $8 "\t" $9 "\t" $10 "\t" $11}' > ./results/best_pred_test_$2.conll

rm ./results/aux

python ./scripts/get_conllu.py ../conlluBarnes/$1/head_final/test.conllu ./results/best_pred_test_$2.conll > ./results/best_pred_test_$2.conllu






