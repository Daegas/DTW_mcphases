> To access the dataset, a data use agreement must be signed: https://physionet.org/content/mcphases/1.0.0/

# About
This project is part of the Data Science Course of the Research Center of Mathematics (CIMAT - Mty 🇲🇽)


# Research Question

> Can differentiated physiological profiles be identified among participants?

This analysis contains an analysis of physiological and hormonal time series from the mcPHASES dataset, with the objective of exploring whether unsupervised machine learning techniques can identify meaningful groupings of menstrual cycles based on wearable sensor measurements and hormone dynamics.

It uses time-series preprocessing, physiological alignment based on the luteinizing hormone (LH) peak, Dynamic Time Warping (DTW), multivariate DTW, hierarchical clustering, K-Medoids clustering, and dimensionality reduction techniques to compare menstrual cycles and evaluate similarities in temporal physiological patterns.

Spoiler: no significant findings were observed with the selected data. Across the different preprocessing strategies, clustering methods, linkage criteria, and alignment approaches evaluated, the resulting clusters did not consistently correspond to the menstrual cycle phases defined in the dataset. Although some local structures and subject-specific similarities emerged, the clusters showed limited agreement with the expected physiological phase labels.

# Requirements - Reproducibility

1. Run `pip install -r requirements.txt`
2. Manually download the data from the official website
3. Rename `example.env` -> `.env` and adjust the paths on the file
   

# Project Structure

```text
.
├── notebooks/
│   ├── ETL.ipynb
│   └── DTW.ipynb
├── output/
├── requirements.txt
├── .env
└── Reporte.pdf
```

* `notebooks/` directory
  Sorry is a bit messy.
  * `ETL.ipynb`
    **Input**: Data
    **Output**: `output/mcphases_consolidated_2022.csv` and images in the format `subject_{subject_id}_physio_signals.png`
    ($n \times p$)

  * `DTW.ipynb`
    **Input**: previous output `df_clean` a bit more cleaning was made in it tho
    Main analysis
* `Reporte.pdf`
  A report with a bit more of the mathematics behind and details/findings.

---

# Use of AI

* ETL:
  * An initial version of the notebook was created with the help of in-line prompts such as:

    * *# max and min frequency of records per subject*
    * *# counts by id*
    * *# plot signals for a subject*
    * Some of these remain as comments in the notebook cells.
  * AI assistance was also used to review and improve the structure, as well as the final CSV consolidation section.
* Script to evaluate different standardization approaches and linkage methods based on the messy code in ETL.
* DTW:
  * Prompts were provided describing the ETL's output structure and the project objectives.
  * Each cell was checked and edited as necessary, we got a lot for help for plotting.



# Future improvements 
There are many like for example increasing the sample size, incorporating additional physiological and behavioral variables, exploring alternative similarity measures beyond DTW, applying feature engineering to extract cycle-level descriptors, evaluating supervised learning approaches for phase prediction.


Personally, I would like to explore the second observation period (2024) and compare it with the first one. My hypothesis is that clustering may be easier during this interval because the physiological and hormonal signals of different subjects could show a greater tendency to synchronize. If this is the case, the time-series patterns may become more similar across subjects, making it easier for DTW-based methods to identify meaningful groups. Problem is that second interval has less subjects.

# References

```bibtex
@dataset{symul2026mcphases,
  author    = {Symul, Laura and others},
  title     = {{mcPHASES: A Dataset of Physiological, Hormonal, and
               Self-reported Events and Symptoms for Menstrual Health
               Tracking with Wearables}},
  year      = {2026},
  version   = {1.0.0},
  publisher = {PhysioNet},
  url       = {https://physionet.org/content/mcphases/1.0.0/}
}
```
