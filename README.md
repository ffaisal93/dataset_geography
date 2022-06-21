# Dataset Geography
This repository walk throughs the approach proposed in our paper: [Dataset Geography: Mapping Language Data to Language Users](https://aclanthology.org/2022.acl-long.239/).

## Steps

### 1. Entity recognition and linking
We use [mGENRE](https://github.com/facebookresearch/GENRE/tree/main/examples_mgenre) to perform both entity recogniton and linking for most of the datasets we experimented with. See [installation, download and example usage](https://github.com/facebookresearch/GENRE/tree/main/examples_mgenre) section to get familier with mGENRE. Once you have mGENRE running on your system, you can use it to extract as well as link dataset to wikidata entites.
Primarily, you need to [install fairseq](https://github.com/facebookresearch/GENRE/tree/main/examples_mgenre#mgenre-for-fairseq) and download the following files which you can obtain following the [mGENRE instructions](https://github.com/facebookresearch/GENRE/tree/main/examples_mgenre#download):
- the pre-trained model
- the prefix tree (trie) from Wikipedia titles
- the dictionary to map the generated strings to Wikidata identifiers
- a mention table to restrict the search space to a number of candidates

Then we use [entity_le.py](https://github.com/ffaisal93/dataset_geography/blob/master/code/entity_le.py) (modified version of mGENRE example codes) to extract the entities given the dataset files(format: pickle file containing dataset texts as a list of string). This script is defined to process 200 sentences at once. Provide the [correct model file paths](https://github.com/ffaisal93/dataset_geography/blob/master/code/entity_le.py#:~:text=model_mlpath%20%3D%20%22../models,lang_title2wikidataID%2Dnormalized_with_redirect.pkl%22) before running.

#### example input dataset format:
```python
import sys
>>> import pickle
>>> datafile="data/sentences/tydiqa/tydiqa-train-english.pickle"
>>> with open(datafile,'rb') as f:
...             sentences =  pickle.load(f)
... 
>>> sentences[:2]
['[START] Is Creole a pidgin of French? [END]', '[START] When was quantum field theory developed? [END]']
```

#### command to extract entities for all the files in `data/sentences/tydiqa/` folder:
```bash
cd ../code
python mgenre_ner.sh ../data/sentences/tydiqa ../data/entities/tydiqa 
```

#### example output entity linked dataset format:
```python
>>> import pickle
>>> outfile="data/entities/tydiqa/tydiqa-train-english.pickle"
>>> with open(outfile,'rb') as f:
...     entities=pickle.load(f)
... 
>>> entities[:2]
[[{'id': 'Q33260', 'texts': ['French-based creole languages >> en'], 'scores': tensor([-0.6672]), 'score': tensor(-2.0017)}, {'id': 'Q33831', 'texts': ['Pidgin >> en'], 'scores': tensor([-0.9490]), 'score': tensor(-2.1220)}, {'id': 'Q33289', 'texts': ['Creole language >> en'], 'scores': tensor([-0.9833]), 'score': tensor(-2.4085)}, {'id': 'Q17093549', 'texts': ['Pidgin English >> en'], 'scores': tensor([-1.3735]), 'score': tensor(-3.3644)}, {'id': 'Q150', 'texts': ['French language >> en'], 'scores': tensor([-1.6143]), 'score': tensor(-3.6097)}], [{'id': 'Q54505', 'texts': ['Quantum field theory >> en'], 'scores': tensor([-0.2873]), 'score': tensor(-0.7602)}, {'id': 'Q899444', 'texts': ['De Broglie–Bohm theory >> en'], 'scores': tensor([-0.3818]), 'score': tensor(-1.3227)}, {'id': 'Q3278166', 'texts': ['History of quantum field theory >> en'], 'scores': tensor([-0.7374]), 'score': tensor(-2.0858)}, {'id': 'Q188403', 'texts': ['History of quantum chemistry >> en'], 'scores': tensor([-0.8181]), 'score': tensor(-2.1645)}, {'id': 'Q730675', 'texts': ['Quantitative research >> en'], 'scores': tensor([-1.0298]), 'score': tensor(-2.5224)}]]
```


### 2. Dataset Country Mapping
We use [plot_geo_tydiqa.py](https://github.com/ffaisal93/dataset_geography/blob/master/code/plot_geo_tydiqa.py) to map dataset entities to geographical entities. Modify [input/output file paths](https://github.com/ffaisal93/dataset_geography/blob/master/code/plot_geo_tydiqa.py#:~:text=for%20LANG%20in,(inp)) and other pointers as you need. We use [plotly](https://plotly.com/python/getting-started/) to create dataset maps. Take a look at the [requirements dump](https://github.com/ffaisal93/dataset_geography/blob/master/requirements.txt) for all additional dependencies.

## Experiments
Additional detailed experiment pointers including ner-relaxed vs ner-constrain results, region-wise performance measurement will be uploaded. 

## Citation
If you use Dataset Geography, please cite the "[Dataset Geography: Mapping Language Data to Language Users](https://aclanthology.org/2022.acl-long.239/)". You can use the following BibTeX entry
~~~
@inproceedings{faisal-etal-2022-dataset,
    title = "Dataset Geography: Mapping Language Data to Language Users",
    author = "Faisal, Fahim  and
      Wang, Yinkai  and
      Anastasopoulos, Antonios",
    booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = may,
    year = "2022",
    address = "Dublin, Ireland",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.acl-long.239",
    doi = "10.18653/v1/2022.acl-long.239",
    pages = "3381--3411",
}
~~~

We built the entity-linked version of the datasets using mGENRE. Kindly also make sure to cite the original mGENRE paper if you use this specific entity linking approach or the already linked datasets using mGENRE,
~~~
@article{de-cao-etal-2022-multilingual,
    title = "Multilingual Autoregressive Entity Linking",
    author = "De Cao, Nicola  and
      Wu, Ledell  and
      Popat, Kashyap  and
      Artetxe, Mikel  and
      Goyal, Naman  and
      Plekhanov, Mikhail  and
      Zettlemoyer, Luke  and
      Cancedda, Nicola  and
      Riedel, Sebastian  and
      Petroni, Fabio",
    journal = "Transactions of the Association for Computational Linguistics",
    volume = "10",
    year = "2022",
    address = "Cambridge, MA",
    publisher = "MIT Press",
    url = "https://aclanthology.org/2022.tacl-1.16",
    doi = "10.1162/tacl_a_00460",
    pages = "274--290",
}
~~~

## License
- Dataset Geography: Apache License 2.0
- mGENRE: CC-BY-NC 4.0
