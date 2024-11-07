# WeLT-TablERT-CNN: Table-filling JNERE Using WeLT

Authors: Ghadeer Mobasher*, Olga Krebs, Wolfgang Müller, and Michael Gertz 


## Installation 
Please make sure to install all the required [dependencies](https://github.com/mobashgr/WeLT-TablERT-CNN/blob/main/requirements.txt).

## Data Preparation
Follow [TablERT-CNN](https://github.com/YoumiMa/TablERT-CNN)'s instructions to properly download data 
-Fetch Data : (CoNLL04)
 ```
 python3 preprocessing/spert2tabcnn.py $SPERT_DATA_DIR data/datasets/conll04/ 
```
## Examples
(1) Train CoNLL04 on train dataset:
```
python run.py train --config configs/train_conll04.conf
```

(2) Evaluation of CoNLL04:

```
python run.py eval --config config/eval_conll04.conf
```

 ## Citation
 The manuscript is in preparation (TBD)

## References
Markus Eberts and Adrian Ulges, 2020, 'Span-based joint entity and relation extraction with transformerpre-training' In 24th European Conference on Artifi-cial Intelligence (ECAI).
Youmi Ma, Tatsuya Hiraoka, and Naoaki Okazaki. Named Entity Recognition and Relation Extraction Using Enhanced Table Filling by Contextualized Representations. 自然言語処理, 29(1):187–223, March 2022. (doi: 10.5715/jnlp.29.187).
Youmi Ma, Tatsuya Hiraoka, and Naoaki Okazaki. Joint Entity and Relation Extraction Based on Table Labeling Using Convolutional Neural Networks. 6th Workshop on Structured Prediction for NLP (SPNLP), May 2022.

## Acknowledgment
Ghadeer Mobasher* is part of the [PoLiMeR-ITN](http://polimer-itn.eu/) and is supported by the European Union’s Horizon 2020 research and innovation program under the Marie Skłodowska-Curie grant agreement PoLiMeR, No 812616.
