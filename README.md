Author: Junhyun Chae  
University of Hyogo  
Research: Multilayer DebtRank Financial Risk Propagation

# Multilayer DebtRank Systemic Risk Analysis

This repository contains the code used for the research on international financial risk propagation using a multilayer network framework.

The model integrates:

- **BIS Locational Banking Statistics (financial layer)**
- **UN Comtrade trade network (trade layer)**

and applies a **DebtRank-based contagion simulation** to analyze cross-country systemic risk propagation.

## Related Paper

Chae, J., & Inoue, H. (2026). Multilayer Propagation of Cross-Country Systemic Risk. *Journal of Risk and Financial Management*, 19(3), 197. https://doi.org/10.3390/jrfm19030197

An earlier version, *A Quantitative Analysis of Financial Distress Propagation in International Networks Utilizing DebtRank and a Multi-layer Approach*, was presented at AROB-ISBC 2025 (Beppu, January 2025) and received the Young Author Award.

```bibtex
@article{chae2026multilayer,
  title   = {Multilayer Propagation of Cross-Country Systemic Risk},
  author  = {Chae, Junhyun and Inoue, Hiroyasu},
  journal = {Journal of Risk and Financial Management},
  volume  = {19},
  number  = {3},
  pages   = {197},
  year    = {2026},
  doi     = {10.3390/jrfm19030197}
}
```

## Author

Junhyun Chae  
Graduate School of Information Science  
University of Hyogo

## Notes

This repository includes:

- DebtRank simulation code
- Leverage matrix construction
- Visualization scripts
- Sensitivity analysis
