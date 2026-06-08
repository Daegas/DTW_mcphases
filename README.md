> Para acceder a los datos se debe firmar un acuerdo de privacidad https://physionet.org/content/mcphases/1.0.0/

# Requierements
`pip install -r requirements.txt`
* Descarga manual de los datos de la página oficial
* Cambiar los paths de los datos y del proyecto


# Archivos en directorio `scripts/`

## ETL.ipynb

**Input**: Data
**Output**: `output/mcphases_consolidated_2022.csv`e imagenes con formato `subject_{subject_id}_physio_signals.png`
  


# Uso de IA
* Se creó una primera versión del ETL con *in-line* prompsts como:
  * *# max and min frequency of records per subject*
  * *# counts by id*
* Luego se pidió revisión y mejorar estructura así como la parte final de consolidación del csv.

# Referencias
```
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