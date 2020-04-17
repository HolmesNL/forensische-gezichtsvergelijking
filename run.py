#!/usr/bin/env python3
import os
from datetime import datetime

import confidence
from lir import CalibratedScorer
from tqdm import tqdm

from lr_face.data_providers import get_data, ImagePairs
from lr_face.evaluators import evaluate
from lr_face.experiment_settings import ExperimentSettings
from lr_face.utils import write_output, parser_setup, process_dataframe
from params import TIMES


def run(args):
    """
    Run one or more calibration experiments.
    The ExperimentSettings class generates a dataframe containing the different parameter combinations called in the
    command line or in params.py.
    """
    experiments_setup = ExperimentSettings(args)
    parameters_used = experiments_setup.input_parameters  # exclude output columns

    experiment_name = datetime.now().strftime("%Y-%m-%d %H %M %S")

    plots_dir = os.path.join('output', experiment_name)
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    # caching for data
    dataproviders = {}

    n_experiments = experiments_setup.data_frame.shape[0]
    for row in tqdm(range(0, n_experiments)):
        params_dict = experiments_setup.data_frame[parameters_used].iloc[row].to_dict()
        data_params = (str(params_dict['datasets']), params_dict['fraction_test'])
        if data_params not in dataproviders:
            dataproviders[data_params] = get_data(**params_dict)
        data_provider = dataproviders[data_params]

        if row < n_experiments / TIMES:
            # for the first round, make plots
            make_plots_and_save_as = os.path.join(plots_dir,
                                                  f"{'_'.join([str(v)[:25] for v in params_dict.values()])}")
            results = experiment(params_dict, data_provider=data_provider,
                                 make_plots_and_save_as=make_plots_and_save_as,
                                 experiment_name=experiment_name)
        else:
            results = experiment(params_dict, data_provider=data_provider)

        for k, v in results.items():
            experiments_setup.data_frame.loc[row, k] = v

    experiments_setup.data_frame = process_dataframe(experiments_setup.data_frame)
    write_output(experiments_setup.data_frame, experiment_name)


def experiment(params, data_provider: ImagePairs = None,
               make_plots_and_save_as=None, experiment_name=None):
    # TODO: naam make_plots_and_save_as veranderen? Nu ook opslaan van data
    """
    Function to run a single experiment with pipeline:
    DataProvider -> fit model on train data -> fit calibrator on calibrator data -> evaluate test set

    """
    lr_system = CalibratedScorer(params['scorers'], params['calibrators'])
    p = lr_system.scorer.predict_proba(data_provider.X_calibrate, data_provider.ids_calibrate)
    lr_system.calibrator.fit(p[:, 1], data_provider.y_calibrate)

    return evaluate(lr_system=lr_system,
                    data_provider=data_provider,
                    params_dict=params,
                    make_plots_and_save_as=make_plots_and_save_as,
                    experiment_name=experiment_name)


if __name__ == '__main__':
    config = confidence.load_name('lr_face')
    parser = parser_setup()
    arg = parser.parse_args()
    run(arg)
