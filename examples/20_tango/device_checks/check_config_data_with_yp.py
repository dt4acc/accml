# Quadrupoles used for tune correction
import pprint

from accml_lib.custom.bessyii.liasion_translator_setup import load_managers

from accml_lib.custom.soleil.manager_setup import load_managers

yp, _, __ = load_managers()
tune_correction_quads = yp.tune_correction_quadrupole_names()
pprint.pp(tune_correction_quads)

from accml_lib.custom.bessyii.liasion_translator_setup import load_managers

bessy_yp, _, __ = load_managers()
tune_correction_quads = bessy_yp.tune_correction_quadrupole_names()

# pprint.pp(tune_correction_quads)