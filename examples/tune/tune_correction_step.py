import jsons
import numpy as np
import yaml
from accml.app.tune.model import TuneResponseCollection


class TuneFit:
    """
    Todo: make interface coherent to scikit learn linear regression
          interface as much as resonable
    """
    def __init__(self, col: TuneResponseCollection):
        self.col = col
        self.x = np.array([item.x.mean for item in col.col])
        self.y = np.array([item.y.mean for item in col.col])
        self.names = [item.pc_name for item  in col.col]

    def predict(self, x, y):
        pass

def main():
    with open("tune_result.yml") as fp:
        d = yaml.safe_load(fp)
    fit = TuneFit(jsons.load(d, TuneResponseCollection))
    fit


if __name__ == "__main__":
    main()