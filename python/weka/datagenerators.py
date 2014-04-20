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

# datagenerators.py
# Copyright (C) 2014 Fracpete (fracpete at gmail dot com)

import javabridge
import logging
import os
import sys
import getopt
import weka.core.jvm as jvm
import weka.core.utils as utils
from weka.core.classes import OptionHandler
from weka.core.dataset import Instances

# logging setup
logger = logging.getLogger("weka.datagenerators")


class DataGenerator(OptionHandler):
    """
    Wrapper class for datagenerators.
    """

    def __init__(self, classname=None, jobject=None):
        """
        Initializes the specified datagenerator using either the classname or the supplied JB_Object.
        :param classname: the classname of the datagenerator
        :param jobject: the JB_Object to use
        """
        if jobject is None:
            jobject = DataGenerator.new_instance(classname)
        if classname is None:
            classname = utils.get_classname(jobject)
        self.classname = classname
        self.enforce_type(jobject, "weka.datagenerators.DataGenerator")
        super(DataGenerator, self).__init__(jobject)

    @classmethod
    def make_data(cls, generator, args):
        """ Generates data using the generator and commandline arguments.
        :rtype : Instances
        :param generator: the generator instance to use
        :param args: the command-line arguments
        """
        return javabridge.static_call(
            "Lweka/datagenerators/DataGenerator;", "makeData",
            "(Lweka/datagenerators/DataGenerator;[Ljava/lang/String;)V",
            generator.jobject, args)


def main(args):
    """
    Runs a datagenerator from the command-line. Calls JVM start/stop automatically.
    Options:
        [-j jar1[:jar2...]]
        [-X max heap size]
        -o output
        [-S seed]
        [-r relation]
        datagenerator classname
        [datagenerator options]
    """

    usage = "Usage: weka.datagenerators [-j jar1[" + os.pathsep + "jar2...]] [-X max heap size] " \
            + "datagenerator classname -o output [-S seed] [-r relation] [datagenerator options]"

    optlist, optargs = getopt.getopt(args, "j:X:h")
    if len(optargs) == 0:
        raise Exception("No datagenerator classname provided!\n" + usage)
    for opt in optlist:
        if opt[0] == "-h":
            print(usage)
            return

    jars = []
    heap = None
    for opt in optlist:
        if opt[0] == "-j":
            jars = opt[1].split(os.pathsep)
        elif opt[0] == "-X":
            heap = opt[1]

    jvm.start(jars, max_heap_size=heap, packages=True)

    logger.debug("Commandline: " + utils.join_options(args))

    try:
        generator = DataGenerator(classname=optargs[0])
        optargs = optargs[1:]
        if len(optargs) > 0:
            generator.set_options(optargs)
        DataGenerator.make_data(generator, optargs)
    except Exception, ex:
        print(ex)
    finally:
        jvm.stop()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception, e:
        print(e)
