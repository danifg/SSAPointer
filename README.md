# SSAPointer
This repository includes the code of the transition-based SSA model described in the paper [Structured Sentiment Analysis as Transition-based Dependency Parsing](). The implementation is based on the SDP parser by Fernández-González and Gómez-Rodríguez (2020) (https://github.com/danifg/SemanticPointer) and reuses part of its code.

### Requirements
This implementation requires Python 2.7, PyTorch 0.3.1 and Gensim >= 0.12.0.
  
### Data
First of all, you need to include in the ``data_ssa`` folder datasets developed by Barnes et al. (2021) [publicly available](https://github.com/jerbarnes/sentiment_graphs/tree/master/data/sent_graphs). Then, use the following script to convert them to the proper input format:

     python ./scripts/get_data.sh 

In addition, you need to include the pre-trained word embeddings in the ``embs`` folder and contextualized token-level representations extracted from mBERT in the ``bert`` folder. The former can be downloaded as follows:

    wget http://vectors.nlpl.eu/repository/20/58.zip (Norwegian)
    wget http://vectors.nlpl.eu/repository/20/32.zip (Basque)
    wget http://vectors.nlpl.eu/repository/20/34.zip (Catalan)
    wget http://vectors.nlpl.eu/repository/20/18.zip (English)

After unzipping each embedding folder in ``embs``, please rename them as ``eu``, ``ca``, ``ds_unis``, ``mpqa`` or ``norec`` (noting that English embeddings must be duplicated for the two English datasets).  Bert-based embeddings can be provided upon request.

### Experiments
To train the model, run the following script:

    ./scripts/run.sh <model_name> <dataset> <encoding>

where we indicate in ``<dataset>`` the ``eu``, ``ca``, ``ds_unis``, ``mpqa`` or ``norec`` dataset used for training, and we choose the ``head_first`` or ``head_final`` dependency-based representation in ``<encoding>``.



To evaluate the best checkpoint on the test sets, first we need to convert the parser's output into the format accepted by the [scorer](https://github.com/jerbarnes/sentiment_graphs/blob/master/src/F1_scorer.py). To achieve that, please run:

	 ./scripts/dag2conllu.sh <dataset> <model_name> <best_epoch>

where we indicate the dataset, model name and the epoch of the checkpoint that obtains the best LF1 on the development set.


Then, just run the following script to evaluate the model in SSA:

    ./scripts/eval.sh <dataset> <encoding> <model_name>
    
Please note that, in order to run the ``eval.sh`` script, a separate virtual environment must be defined in Python 3 (since the evaluation script developed by Barnes et al. (2021) does not work on Python 2.7).


### Citation

    
    
### Acknowledgments
We acknowledge grants SCANNER-UVIGO (PID2020-113230RB-C22) funded by MICIU/AEI/10.13039/501100011033, and LATCHING-UVIGO (PID2023-147129OB-C22) funded by MICIU/AEI/10.13039/501100011033 and ERDF/EU. 

### Contact
If you have any suggestion, inquiry or bug to report, please contact danifg@uvigo.es.
