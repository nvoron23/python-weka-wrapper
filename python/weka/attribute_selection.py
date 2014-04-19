# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# attribute_selection.py
# Copyright (C) 2014 Fracpete (fracpete at gmail dot com)

import javabridge
import logging
import os
import sys
import getopt
import weka.core.jvm as jvm
import weka.core.utils as utils
import weka.core.arrays as arrays
from weka.core.classes import JavaObject
from weka.core.classes import OptionHandler
from weka.core.capabilities import Capabilities
from weka.core.dataset import Instances, Instance

# logging setup
logger = logging.getLogger("weka.attribute_selection")


class ASSearch(OptionHandler):
    """
    Wrapper class for attribute selection search algorithm.
    """

    def __init__(self, classname=None, jobject=None):
        """
        Initializes the specified search algorithm using either the classname or the supplied JB_Object.
        :param classname: the classname of the search algorithms
        :param jobject: the JB_Object to use
        """
        if jobject is None:
            jobject = ASSearch.new_instance(classname)
        if classname is None:
            classname = utils.get_classname(jobject)
        self.classname = classname
        self.enforce_type(jobject, "weka.attributeSelection.ASSearch")
        super(ASSearch, self).__init__(jobject)

    def search(self, evaluation, data):
        """
        Performs the search and returns the indices of the selected attributes.
        :param evaluation: the evaluation algorithm to use
        :param data: the data to use
        :rtype: ndarray
        """
        array = javabridge.call(
            self.jobject, "search", "(Lweka/attributeSelection/ASEvaluation;Lweka/core/Instances;)[I",
            evaluation.jobject, data.jobject)
        if array is None:
            return None
        else:
            jvm.ENV.get_int_array_elements(array)


class ASEvaluation(OptionHandler):
    """
    Wrapper class for attribute selection evaluation algorithm.
    """

    def __init__(self, classname=None, jobject=None):
        """
        Initializes the specified search algorithm using either the classname or the supplied JB_Object.
        :param classname: the classname of the search algorithms
        :param jobject: the JB_Object to use
        """
        if jobject is None:
            jobject = ASEvaluation.new_instance(classname)
        if classname is None:
            classname = utils.get_classname(jobject)
        self.classname = classname
        self.enforce_type(jobject, "weka.attributeSelection.ASEvaluation")
        super(ASEvaluation, self).__init__(jobject)

    def get_capabilities(self):
        """
        Returns the capabilities of the classifier.
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

    def build_evaluator(self, data):
        """
        Builds the evaluator with the data.
        :param data: the data to use
        """
        javabridge.call(self.jobject, "buildEvaluator", "(Lweka/core/Instances;)V", data.jobject)

    def post_process(self, indices):
        """
        Post-processes the evaluator with the selected attribute indices.
        :param indices: the attribute indices list to use
        :rtype: ndarray
        """
        array = javabridge.call(self.jobject, "postProcess", "([I)[I", indices)
        if array is None:
            return None
        else:
            return jvm.ENV.get_int_array_elements(array)


class AttributeSelection(JavaObject):
    """
    Performs attribute selection using search and evaluation algorithms.
    """

    def __init__(self):
        """
        Initializes the attribute selection.
        """
        jobject = AttributeSelection.new_instance("weka.attributeSelection.AttributeSelection")
        super(AttributeSelection, self).__init__(jobject)

    def set_evaluator(self, evaluator):
        """
        Sets the evaluator to use.
        :param evaluator: the evaluator to use.
        """
        javabridge.call(self.jobject, "setEvaluator", "(Lweka/attributeSelection/ASEvaluation;)V", evaluator.jobject)

    def set_search(self, search):
        """
        Sets the search algorithm to use.
        :param search: the search algorithm
        """
        javabridge.call(self.jobject, "setSearch", "(Lweka/attributeSelection/ASSearch;)V", search.jobject)

    def set_folds(self, folds):
        """
        Sets the number of folds to use for cross-validation.
        :param folds: the number of folds
        """
        javabridge.call(self.jobject, "setFolds", "(I)V", folds)

    def set_ranking(self, ranking):
        """
        Sets whether to perform a ranking, if possible.
        :param ranking: whether to perform a ranking
        """
        javabridge.call(self.jobject, "setRanking", "(Z)V", ranking)

    def set_seed(self, seed):
        """
        Sets the seed for cross-validation.
        :param seed: the seed value
        """
        javabridge.call(self.jobject, "setSeed", "(I)V", seed)

    def set_crossvalidation(self, crossvalidation):
        """
        Sets whether to perform cross-validation.
        :param crossvalidation: whether to perform cross-validation
        """
        javabridge.call(self.jobject, "setXval", "(Z)V", crossvalidation)

    def select_attributes(self, instances):
        """
        Performs attribute selection on the given dataset.
        :param instances: the data to process
        """
        javabridge.call(self.jobject, "SelectAttributes", "(Lweka/core/Instances;)V", instances.jobject)

    def select_attributes_cv_split(self, instances):
        """
        Performs attribute selection on the given cross-validation split.
        :param instances: the data to process
        """
        javabridge.call(self.jobject, "selectAttributesCVSplit", "(Lweka/core/Instances;)V", instances.jobject)

    def get_selected_attributes(self):
        """
        Returns the selected attributes from the last run.
        :rtype: ndarray
        """
        array = javabridge.call(self.jobject, "selectedAttributes", "()[I")
        if array is None:
            return None
        else:
            return jvm.ENV.get_int_array_elements(array)

    def to_results_string(self):
        """
        Generates a results string from the last attribute selection.
        :rtype: str
        """
        return javabridge.call(self.jobject, "toResultsString", "()Ljava/lang/String;")

    def get_cv_results_string(self):
        """
        Generates a results string from the last cross-validation attribute selection.
        :rtype: str
        """
        return javabridge.call(self.jobject, "CVResultsString", "()Ljava/lang/String;")

    def get_number_attributes_selected(self):
        """
        Returns the number of attributes that were selected.
        :rtype: int
        """
        return javabridge.call(self.jobject, "numberAttributesSelected", "()I")

    def get_ranked_attributes(self):
        """
        Returns the matrix of ranked attributes from the last run.
        :rtype: ndarray
        """
        matrix = javabridge.call(self.jobject, "rankedAttributes", "()[[D")
        if matrix is None:
            return None
        else:
            return arrays.double_matrix_to_ndarray(matrix)

    def reduce_dimensionality(self, data):
        """
        Reduces the dimensionality of the provided Instance or Instances object.
        :rtype: same as input
        """
        if type(data) is Instance:
            return Instance(
                javabridge.call(
                    self.jobject, "reduceDimensionality",
                    "(Lweka/core/Instance;)Lweka/core/Instance;", data.jobject))
        else:
            return Instances(
                javabridge.call(
                    self.jobject, "reduceDimensionality",
                    "(Lweka/core/Instances;)Lweka/core/Instances;", data.jobject))

    @classmethod
    def attribute_selection(cls, evaluator, args):
        """
        Performs attribute selection using the given attribute evaluator and options.
        :param evaluator: the evaluator to use
        :param args: the command-line args for the attribute selection
        :rtype; str
        """
        return javabridge.static_call(
            "Lweka/attributeSelection/AttributeSelection;", "SelectAttributes",
            "(Lweka/attributeSelection/ASEvaluation;[Ljava/lang/String;)Ljava/lang/String;",
            evaluator.jobject, args)


def main(args):
    """
    Runs attribute selection from the command-line. Calls JVM start/stop automatically.
    Options:
        -j jar1[:jar2...]
        -i train
        [-c classindex]
        [-s search method]
        [-x num folds]
        [-n seed]
        evaluator classname
    """

    usage = "Usage: weka.attribute_selection -j jar1[" + os.pathsep + "jar2...] -i input file [-c classindex] " \
            + "[-s search method][-x num folds] [-n seed] " \
            + "evaluator classname [evaluator options]"

    optlist, optargs = getopt.getopt(args, "j:i:c:s:x:n:")
    if len(optargs) == 0:
        raise Exception("No evaluator classname provided!\n" + usage)
    for opt in optlist:
        if opt[0] == "-h":
            print(usage)
            return

    jars   = []
    params = []
    input  = None
    search = None
    for opt in optlist:
        if opt[0] == "-j":
            jars = opt[1].split(os.pathsep)
        elif opt[0] == "-i":
            params.append(opt[0])
            params.append(opt[1])
            input = opt[1]
        elif opt[0] == "-c":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-s":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-x":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-n":
            params.append(opt[0])
            params.append(opt[1])

    # check parameters
    if input is None:
        raise Exception("No input file provided ('-i ...')!")

    jvm.start(jars)

    logger.debug("Commandline: " + utils.join_options(args))

    try:
        evaluation = ASEvaluation(classname=optargs[0])
        optargs = optargs[1:]
        if len(optargs) > 0:
            evaluation.set_options(optargs)
        print(AttributeSelection.attribute_selection(evaluation, params))
    except Exception, e:
        print(e)
    finally:
        jvm.stop()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception, e:
        print(e)