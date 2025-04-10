# Analog-EGAT-SymExtract #
The corresponding code for the article "Graph Attention-Based Symmetry Constraint Extraction for Analog Circuits"
# how to use #
- run my_parser first
- run my_readgraph then
- run my_egat_model_test finally
- **remember add your filepath**
# example #
1.set conda env
- conda activate egat
2.run my_parser, 'dataXY_file.txt' will be saved in '../my_readgraph'
- python3 my_readgraph/my_parser.py
3.run my_readgraph, data will be saved in '../my_readgraph'
- python3 my_readgraph/my_readgraph.py
4.run my_egat_model_test finally, model will be saved and then test the result
- CUDA_VISIBLE_DEVICES=1 python3 my_readgraph/my_egat_model_test.py