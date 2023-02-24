# Description

The following script allows to convert ann data into .spacy data for training purposes of NER models. 
It's also possible to use processing methods like removing stopwords to get possibly better training results. 
The indices of entities can also be detected again if a preprocessing step has been used that changes the indices of the entities. 

# Background informations

I wrote the script for a text mining uni course. 
The purpose was to train a model that detects specific entities in German medical documents. 
Removing the special characters and converting the umlauts from the data were the most effective preprocessing methods for my use case.
