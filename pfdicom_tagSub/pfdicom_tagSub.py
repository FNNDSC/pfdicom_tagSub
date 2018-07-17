# System imports
import      os
import      getpass
import      argparse
import      json
import      pprint
import      csv

# Project specific imports
import      pfmisc
from        pfmisc._colors      import  Colors
from        pfmisc              import  other
from        pfmisc              import  error

import      pudb
import      pftree
import      pfdicom

class pfdicom_tagSub(pfdicom.pfdicom):
    """

    A class based on the 'pfdicom' infrastructure that extracts 
    and processes DICOM tags according to several requirements.

    Powerful output formatting, such as image conversion to jpg/png
    and generation of html reports is also supported.

    """

    def declare_selfvars(self):
        """
        A block to declare self variables
        """

        #
        # Object desc block
        #
        self.str_desc                   = ''
        self.__name__                   = "pfdicom_tagExtract"

        # Tags
        self.b_tagList                  = False
        self.b_tagFile                  = False
        self.str_tagStruct              = ''
        self.str_tagFile                = ''
        self.d_tagStruct                = {}

        self.dp                         = None
        self.log                        = None
        self.tic_start                  = 0.0
        self.pp                         = pprint.PrettyPrinter(indent=4)
        self.verbosityLevel             = -1

    def __init__(self, *args, **kwargs):
        """
        A "base" class for all pfdicom objects. This class is typically never 
        called/used directly; derived classes are used to provide actual end
        functionality.

        This class really only reads in a DICOM file, and populates some
        internal convenience member variables.

        Furthermore, this class does not have a concept nor concern about 
        "output" relations.
        """

        def tagStruct_process(str_tagStruct):
            self.d_tagStruct            = json.loads(str_tagStruct)

        def tagFile_process(str_tagFile):
            self.str_tagFile            = str_tagFile
            if len(self.str_tagFile):
                self.b_tagFile          = True
                with open(self.str_tagFile) as f:
                    self.d_tagStruct    = json.load(f)

        def outputFile_process(str_outputFile):
            self.str_outputFileType     = str_outputFile

        # pudb.set_trace()
        self.declare_selfvars()

        # Process some of the kwargs by the base class
        super().__init__(*args, **kwargs)

        for key, value in kwargs.items():
            if key == "outputFileType":     outputFile_process(value) 
            if key == 'tagFile':            tagFile_process(value)
            if key == 'tagStruct':          tagStruct_process(value)
            if key == 'verbosity':          self.verbosityLevel         = int(value)

        # Set logging
        self.dp                        = pfmisc.debug(    
                                            verbosity   = self.verbosityLevel,
                                            level       = 0,
                                            within      = self.__name__
                                            )
        self.log                       = pfmisc.Message()
        self.log.syslog(True)

    def filelist_prune(self, at_data, *args, **kwargs):
        """
        Given a list of files, possibly prune list by 
        extension.
        """
        if len(self.str_extension):
            al_file = at_data[1]
            al_file = [x for x in al_file if self.str_extension in x]
        return {
            'status':   True,
            'l_file':   al_file
        }

    def tags_process(self, *args, **kwargs):
        """
        Process the tag information for each file in this pass.
        """

        str_path            = ''
        l_file              = []
        b_status            = True

        # These are declared in the base class
        self.dcm            = None
        self.d_dcm          = {}
        self.d_dicom        = {}
        self.d_dicomSimple  = {}

        # list structure to track all dcm objects processed 
        # in this path
        l_dcm               = []

        for k, v in kwargs.items():
            if k == 'l_file':   l_file      = v
            if k == 'path':     str_path    = v

        if len(args):
            at_data         = args[0]
            str_path        = at_data[0]
            l_file          = at_data[1]

        for f in l_file:

            d_DCMfileRead   = self.DICOMfile_read( 
                                    file        = '%s/%s' % (str_path, f)
            )
            b_status        = b_status and d_DCMfileRead['status']
            l_tagsToUse     = d_DCMfileRead['l_tagsToUse']      
            if b_status:
                for k, v in self.d_tagStruct.items():
                    d_tagsInStruct  = self.tagsInString_process(v)
                    str_tagValue    = d_tagsInStruct['str_result']
                    setattr(self.dcm, k, str_tagValue)
                l_dcm.append(self.dcm)

        return {
            'status':           b_status,
            'l_dcm':            l_dcm,
            'l_file':           l_file,
            'str_path':         d_DCMfileRead['inputPath'],
        }

    def outputSave(self, at_data, **kwags):
        """
        Callback for saving outputs.
        """

        d_outputInfo        = at_data[1]
        str_outputImageFile = ""
        d_convertToImg      = {}
        path                = at_data[0]
        str_cwd             = os.getcwd()
        other.mkdir(self.str_outputDir)
        self.dp.qprint("In output base directory:     %s" % self.str_outputDir)
        os.chdir(self.str_outputDir)
        other.mkdir(path)
        os.chdir(path)

        for f, ds in zip(d_outputInfo['l_file'], d_outputInfo['l_dcm']):
            ds.save_as(f)
            self.dp.qprint("saving in path: %s" % path)
            self.dp.qprint("DICOM file:     %s" % f)

        os.chdir(str_cwd)
        return {
            'status':   True
        }

    def run(self, *args, **kwargs):
        """
        The run method demonstrates how to correctly call 
        sub-components relating to the program execution.
        """
        b_status        = True
        d_pftreeRun     = {}
        d_inputAnalysis = {}
        d_tagSub        = {}
        d_env           = self.env_check()

        if d_env['status']:
            d_pftreeRun = self.pf_tree.run()
        else:
            b_status    = False 

        str_startDir    = os.getcwd()
        os.chdir(self.str_inputDir)
        if b_status:
            d_inputAnalysis = self.pf_tree.tree_analysisApply(
                                analysiscallback        = self.filelist_prune,
                                applyResultsTo          = 'inputTree',
                                applyKey                = 'l_file',
                                persistAnalysisResults  = True
            )
            d_tagSub        = self.pf_tree.tree_analysisApply(
                                analysiscallback        = self.tags_process,
                                outputcallback          = self.outputSave,
                                persistAnalysisResults  = False
            )

        os.chdir(str_startDir)
        return {
            'status':           b_status and d_pftreeRun['status'],
            'd_env':            d_env,
            'd_pftreeRun':      d_pftreeRun,
            'd_tagSub':         d_tagSub,
            'd_inputAnalysis':  d_inputAnalysis
        }
        