#!/usr/bin/env bash
#CUDA_VISIBLE_DEVICES=2 
python scripts/L2RParser.py --mode FastLSTM --num_epochs 500 --batch_size 32 --decoder_input_size 256 --hidden_size 512 --encoder_layers 3 --decoder_layers 1 \
 --pos_dim 100 --char_dim 100 --lemma_dim 100 --num_filters 100 --arc_space 512 --type_space 128 \
 --opt adam --learning_rate 0.001 --decay_rate 0.75 --epsilon 1e-4 --coverage 0.0 --gamma 0.0 --clip 5.0 \
 --schedule 20 --double_schedule_decay 5 \
 --p_in 0.33 --p_out 0.33 --p_rnn 0.33 0.33 --unk_replace 0.5 --label_smooth 1.0 --char \
 --word_embedding sskip --word_path "./embs/"$2"/model.txt.gz" --char_embedding random \
  --train "./data_dag/"$2"_"$3"_train.dag" \
   --dev "./data_dag/"$2"_"$3"_dev.dag" \
   --test "./data_dag/"$2"_"$3"_test.dag" \
   --test2 "./data_dag/"$2"_test2.dag" \
   --model_path "./models/"$1"/" --model_name 'network.pt'    --grandPar --lemma --beam 5 \
    --bert_path_train "./bert/"$2"_train.mbertbase.cased" \
    --bert_path_dev "./bert/"$2"_dev.mbertbase.cased" \
    --bert_path_test "./bert/"$2"_test.mbertbase.cased" \
    --bert_path_test2 "./bert/"$2"_test2.mbertbase.cased" \
    --bert --bert_dim 768 --pos > $1



