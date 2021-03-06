# DKFZ
#
#
# Copyright (c) German Cancer Research Center,
# Division of Medical Image Computing.
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE

import os
import logging
import optunity
import warnings
from pprint import pformat
from hyppopy.globals import DEBUGLEVEL

LOG = logging.getLogger(os.path.basename(__file__))
LOG.setLevel(DEBUGLEVEL)

from hyppopy.solvers.HyppopySolver import HyppopySolver


class OptunitySolver(HyppopySolver):

    def __init__(self, project=None):
        HyppopySolver.__init__(self, project)
        self._solver_info = None
        self.opt_trials = None

    def loss_function_call(self, params):
        for key in params.keys():
            if self.project.get_typeof(key) is int:
                params[key] = int(round(params[key]))
        return self.blackbox(**params)

    def execute_solver(self, searchspace):
        LOG.debug("execute_solver using solution space:\n\n\t{}\n".format(pformat(searchspace)))
        try:
            self.best, _, _ = optunity.minimize_structured(f=self.loss_function,
                                                           num_evals=self.max_iterations,
                                                           search_space=searchspace)
        except Exception as e:
            LOG.error("internal error in optunity.minimize_structured occured. {}".format(e))
            raise BrokenPipeError("internal error in optunity.minimize_structured occured. {}".format(e))

    def split_categorical(self, pdict):
        categorical = {}
        uniform = {}
        for name, pset in pdict.items():
            for key, value in pset.items():
                if key == 'domain' and value == 'categorical':
                    categorical[name] = pset
                elif key == 'domain':
                    if value != 'uniform':
                        msg = "Warning: Optunity cannot handle {} domain. Only uniform and categorical domains are supported!".format(value)
                        warnings.warn(msg)
                        LOG.warning(msg)
                    uniform[name] = pset
        return categorical, uniform

    def convert_searchspace(self, hyperparameter):
        LOG.debug("convert input parameter\n\n\t{}\n".format(pformat(hyperparameter)))
        solution_space = {}
        # split input in categorical and non-categorical data
        cat, uni = self.split_categorical(hyperparameter)
        # build up dictionary keeping all non-categorical data
        uniforms = {}
        for key, value in uni.items():
            for key2, value2 in value.items():
                if key2 == 'data':
                    if len(value2) == 3:
                        uniforms[key] = value2[0:2]
                    elif len(value2) == 2:
                        uniforms[key] = value2
                    else:
                        raise AssertionError("precondition violation, optunity searchspace needs list with left and right range bounds!")

        if len(cat) == 0:
            return uniforms
        # build nested categorical structure
        inner_level = uniforms
        for key, value in cat.items():
            tmp = {}
            tmp2 = {}
            for key2, value2 in value.items():
                if key2 == 'data':
                    for elem in value2:
                        tmp[elem] = inner_level
            tmp2[key] = tmp
            inner_level = tmp2
        solution_space = tmp2
        return solution_space
