# Analog-EGAT-SymExtract #
The corresponding code for the article "Graph Attention-Based Symmetry Constraint Extraction for Analog Circuits"
# how to use #
- run my_parser first
- run my_readgraph then
- run my_egat_model_test finally
- **remember add your filepath**
# example #
This file contains three OTA circuits with labels for testing purposes.
- run my_parser, 'dataXY_file.txt' will be saved in '../my_readgraph'
python3 my_readgraph/my_parser.py
- run my_readgraph, data will be saved in '../my_readgraph'
python3 my_readgraph/my_readgraph.py
- run my_egat_model_test finally, model will be saved and then test the result
CUDA_VISIBLE_DEVICES=1 python3 my_readgraph/my_egat_model_test.py
