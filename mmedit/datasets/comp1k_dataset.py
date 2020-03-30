import os.path as osp
from pathlib import Path

import mmcv

from .base_matting_dataset import BaseMattingDataset
from .registry import DATASETS


@DATASETS.register_module
class AdobeComp1kDataset(BaseMattingDataset):
    """Adobe comp-1k dataset.

    The dataset loads (alpha, fg, bg) data and apply specified transforms to
    the data. You could specify whether composite merged image online or load
    composited merged image in pipeline.

    Example for online comp-1k dataset:
    ```
    [
        {
            "alpha": 'alpha/000.png',
            "fg": 'fg/000.png',
            "bg": 'bg/000.png'
        },
        {
            "alpha": 'alpha/001.png',
            "fg": 'fg/001.png',
            "bg": 'bg/001.png'
        },
    ]
    ```

    Example for offline comp-1k dataset:
    ```
    [
        {
            "alpha": 'alpha/000.png',
            "merged": 'merged/000.png',
            "fg": 'fg/000.png',
            "bg": 'bg/000.png'
        },
        {
            "alpha": 'alpha/001.png',
            "merged": 'merged/001.png',
            "fg": 'fg/001.png',
            "bg": 'bg/001.png'
        },
    ]
    ```
    """

    def load_annotations(self):
        data_infos = mmcv.load(self.ann_file)

        for data_info in data_infos:
            for key in data_info:
                data_info[key] = osp.join(self.data_prefix, data_info[key])

        return data_infos

    def format_results(self, results):
        """Gathering predicted alpha matte from output of the model.

        Args:
            results (list[tuple]): The output of forward_test() of the model.

        Return:
            alphas (dict): Mapping from input image (merged) name to predicted
                alpha.
        """
        alphas = dict()
        print('Gathering predicted alpha matte...')
        prog_bar = mmcv.ProgressBar(len(self))
        cur = 0
        for res in results:
            img_name = Path(self.data_infos[cur]['merged']).name
            alphas[img_name] = res[0] * 255
            cur += 1
            prog_bar.update()
        return alphas