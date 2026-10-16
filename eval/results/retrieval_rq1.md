| config | source | n | Hit@5 | Recall@10 | MRR@10 | DRM@5 | Hit@5 (Khoản) | ms |
|---|---|---|---|---|---|---|---|---|
| clause_header/bm25 | zalo | 81 | 0.753 | 0.819 | 0.699 | 0.143 | – | 13 |
| clause_header/bm25 | all | 146 | 0.842 | 0.886 | 0.748 | 0.119 | 0.791 | 12 |
| clause_header/bm25 | synthetic | 65 | 0.954 | 0.969 | 0.810 | 0.089 | 0.791 | 12 |
| clause_header/dense | zalo | 81 | 0.827 | 0.854 | 0.726 | 0.101 | – | 143 |
| clause_header/dense | all | 146 | 0.897 | 0.919 | 0.822 | 0.079 | 0.977 | 143 |
| clause_header/dense | synthetic | 65 | 0.985 | 1.000 | 0.942 | 0.052 | 0.977 | 142 |
| clause_header/hybrid | zalo | 81 | 0.815 | 0.866 | 0.717 | 0.104 | – | 144 |
| clause_header/hybrid | all | 146 | 0.890 | 0.926 | 0.806 | 0.084 | 0.907 | 146 |
| clause_header/hybrid | synthetic | 65 | 0.985 | 1.000 | 0.917 | 0.058 | 0.907 | 149 |
| clause_header/hybrid_rerank | zalo | 81 | 0.827 | 0.866 | 0.785 | 0.084 | – | 5353 |
| clause_header/hybrid_rerank | all | 146 | 0.904 | 0.926 | 0.871 | 0.070 | 0.930 | 5562 |
| clause_header/hybrid_rerank | synthetic | 65 | 1.000 | 1.000 | 0.978 | 0.052 | 0.930 | 5822 |
