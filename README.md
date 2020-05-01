Forensische Gezichtsvergelijking
=======
Research project to investigate algorithms that can supplement expert opinion in forensic face comparison

--

### Folders
- deepface package: fork from the deepface github (https://github.com/serengil/deepface)
- lr_face package: scripts to initiate the data providers, experiment settings and evaluators
- output folder: generated figures and result files
- resources folder: datasets. Should have resources/enfsi/2011/-copy all images from that folder in the dataset-
- tests folder: TBD
### scripts
- run.py: run the whole pipeline
- run_data_exploration.py: code to make plots
- params.py: settings for experiments
- README.md: this file
- requirements.txt: python packages required


### Pipeline
#### Overview
When running the pipeline:
- first the data is generated/loaded.
- an experiments dataframe is created, containing all combinations of data and parameters to be executed.
- the experiments are run and their results saved in the same dataframe.
- after all the experiments are done, they are evaluated and an output file is created in the `output` folder.

#### Data

##### Calibrators
The calibrator to be used:
- 'dummy': BaseCalibrator(), # Dummy
- 'logit': LogitCalibrator(),
- 'logit_normalized': NormalizedCalibrator(LogitCalibrator()),
- 'logit_unweighted': LogitCalibrator(class_weight=None),
- 'KDE': KDECalibrator(),
- 'elub_KDE': ELUBbounder(KDECalibrator()),
- 'elub': ELUBbounder(BaseCalibrator()),
- 'fraction': FractionCalibrator(),
- 'isotonic': IsotonicCalibrator()

#### Evaluation
##### Metrics
A number of metrics are currently implemented to evaluate the performance of the pipeline:

Capacity to distinguish between h1 and h2 distributions:
- 'cllr' + label: round(calculate_cllr(X1, X2).cllr, 4),

Specifically for the model:
- auc
- accuracy

##### Streamlit
The outcome of the pipeline can be visualised using the Streamlit app. Specify the desired hypothesis you want to test in `run_data_exploration.py`. Adding new hypotheses and code blocks for the plots can be done in this file as well.

The results from the ENFSI proficiency tests (Proficiency_test.xlsx) should be 
added to the resources/enfsi folder.

To use the streamlit app, write in terminal: `streamlit run run_data_exploration.py`


### Labeling

For labeling we will use label-studio, which can be installed via pip. In order to set up you labeling project 
use the following commands: 

```
label-studio init annotations/<project-id> \          
    --input-path <path/to/images>  \
    --input-format image-dir \
    --label-config label-studio.xml

label-studio start annotations/<project-id>
```

You can then start labeling at localhost:8200, your labels will be saved in the annotations/<project-id> folder. 
(It might automatically open localhost:8200/start, remove the /start to start labeling in that case). 

