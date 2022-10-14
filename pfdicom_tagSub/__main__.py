#!/usr/bin/env python3
#
# (c) 2018 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../pfdicom_tagSub'))

try:
    from    .               import pfdicom_tagSub
    from    .               import __pkg, __version__
except:
    from pfdicom_tagSub     import pfdicom_tagSub
    from __init__           import __pkg, __version__


from    argparse            import RawTextHelpFormatter
from    argparse            import ArgumentParser
import  pudb

import  pfmisc
from    pfmisc._colors      import Colors
from    pfmisc              import other

import  pfdicom
from    pfdicom.__main__    import package_CLIfull as pfdicom_CLIfull
from    pfdicom.__main__    import package_argsSynopsisFull as pfdicom_argSynopsis
from    pfdicom.__main__    import parser as pfdicom_parser

str_desc = Colors.CYAN + """

            __    _ _                       _               _____       _
           / _|  | (_)                     | |             /  ___|     | |
     _ __ | |_ __| |_  ___  ___  _ __ ___  | |_  __ _  __ _\ `--. _   _| |__
    | '_ \|  _/ _` | |/ __|/ _ \| '_ ` _ \ | __|/ _` |/ _` |`--. \ | | | '_ \.
    | |_) | || (_| | | (__| (_) | | | | | || |_| (_| | (_| /\__/ / |_| | |_) |
    | .__/|_| \__,_|_|\___|\___/|_| |_| |_| \__|\__,_|\__, \____/ \__,_|_.__/
    | |                                 ______         __/ |
    |_|                                |______|       |___/




                        Path-File DICOM tag substiution

        Recursively walk down a directory tree and process DICOM tags,
        saving each source DICOM in an output tree that  preserves the
        input directory structure.

        Basically a DICOM anonymizer.

                             -- version """ + \
             Colors.YELLOW + __version__ + Colors.CYAN + """ --

        'pfdicom_tagSub' is a customizable and friendly DICOM tag substitutor.
        As part of the "pf*" suite of applications, it is geared to IO as
        directories. Input DICOM trees are reconstructed in an output
        directory, preserving directory structure. Each node tree contains
        a copy of the original DICOM with a user-specified tag list changed
        in the output.

        `pfdicom_tagSub` is typically called with a JSON structure defining
        the DICOM tag name to substitute, along with the substitute value.
        Individual tags can be explicitly referenced, as well as a regular
        expression construct to capture all tags satisfying that expression.
        This allows for capturing all tags with a certain string pattern
        without needing to explicitly list every confirming tag.


""" + Colors.NO_COLOUR

packageCLI_self     = '''
        [--tagStruct <tagStruct>]                                               \\
        [--tagInfo <tagInfo>]                                                   \\
        [--splitToken <token>]                                                  \\
        [--splitKey <keySplit>]                                                 \\'''

package_argsSynopsisSelf = """
        [-T|--tagStruct <JSONtagStructure>]
        Parse the tags and their "subs" from a JSON formatted <JSONtagStucture>
        string passed directly in the command line. Note that sometimes protecting
        a JSON string can be tricky, especially when used in scripts or as variable
        expansions. If the JSON string is problematic, use the [--tagInfo <string>]
        instead.

        [--tagInfo <delimited_parameters>]
        A token delimited string that is reconstructed into a JSON structure by the
        script. This is often useful if the [--tagStruict] JSON string is hard to
        parse in scripts and variable passing within scripts. The format of this
        string is:

        "<tag1><splitKeyValue><value1><split_token><tag2><splitKeyValue><value2>"

        for example:

                --splitToken ","                                                \\
                --splitKeyValue ':'                                             \\
                --tagInfo "PatientName:anon,PatientID:%_md5|7_PatientID"

        or more complexly (esp if the ':' is part of the key):

                --splitToken "++"                                               \\
                --splitKeyValue "="                                             \\
                --tagInfo "PatientBirthDate = %_strmsk|******01_PatientBirthDate ++
                           re:.*hysician"   = %_md5|4_#tag"


        [-s|--splitToken <split_token>]
        The token on which to split the <delimited_parameters> string.
        Default is '++'. Take care with how this is quoted, esp as regards padded
        spaces!

        [-k|--splitKeyValue <keyValueSplit>]
        The token on which to split the <key> <value> pair. Default is ':'
        but this can be problematic if the <key> itself has a ':' (for example
        in the regular expression expansion).
"""

package_CLIfull             = packageCLI_self       + pfdicom_CLIfull
package_argsSynopsisFull    = pfdicom_argSynopsis   + package_argsSynopsisSelf

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  """
    NAME

        pfdicom_tagSub

    SYNOPSIS

        pfdicom_tagSub \ """ + package_CLIfull + """

    BRIEF EXAMPLE

        pfdicom_tagSub                                                          \\
            --fileFilter dcm                                                    \\
            --inputDir /var/www/html/normsmall                                  \\
            --outputDir /var/www/html/anon                                      \\
            --tagStruct '
            {
                "PatientName":              "%_name|patientID_PatientName",
                "PatientID":                "%_md5|7_PatientID",
                "AccessionNumber":          "%_md5|8_AccessionNumber",
                "PatientBirthDate":         "%_strmsk|******01_PatientBirthDate",
                "re:.*hysician":            "%_md5|4_#tag",
                "re:.*stitution":           "#tag",
                "re:.*ddress":              "#tag"
            }
            ' --threads 0 --printElapsedTime
    """

    description =  '''
    DESCRIPTION

        ``pfdicom_tagSub`` replaces a set of ``<tag, value>`` pairs in a DICOM
        header with values passed in a JSON structure (either from the CLI or
        read from a JSON file).

        Individual DICOM tags can be explicitly referenced in the JSON structure,
        as well as a regular expression construct to capture all tags satisfying
        that expression  (allowing for idiomatic bulk substitution of
        ``<tag, value>`` pairs).

        Tag regular expression constructs are ``python`` string expressions and
        are prefixed by ``"re:<pythonRegex>"``. For example, ``"re:.*hysician"``
        will perform some substitution on all tags that contain the letters
        ``hysician``. The value substitution has access to a special lookup,
        ``#tag``, which is the current tag hit. It is possible to apply built in
        functions to the tag hit, for example ``md5`` hashing, using
        ``"%_md5|4_#tag"``,

            {
                "re:.*hysician":                "%_md5|4_#tag"
            }

        will be expanded to


            {
                "PerformingPhysiciansName" :    "%_md5|4_PerformingPhysiciansName"
                "PhysicianOfRecord"        :    "%_md5|4_PhysicianOfRecord"
                "ReferringPhysiciansName"  :    "%_md5|4_ReferringPhysiciansName"
                "RequestingPhysician"      :    "%_md5|4_RequestingPhysician"
            }

        The tag regular expression construct allows for simple and powerful bulk
        substition of ``<tag, value>`` pairs.

        The script accepts an ``<inputDir>``, and then from this point an
        ``os.walk()`` is performed to extract all the subdirs. Each subdir is
        examined for DICOM files (in the simplest sense by a file extension mapping)
        are passed to a processing method that reads and replaces specified
        DICOM tags, saving the result in a corresponding directory and filename
        in the output tree.

    ARGS ''' + package_argsSynopsisFull + '''


    EXAMPLES

    Perform a DICOM anonymization by processing specific tags:

        pfdicom_tagSub                                                          \\
            --fileFilter dcm                                                    \\
            --inputDir /var/www/html/normsmall                                  \\
            --outputDir /var/www/html/anon                                      \\
            --tagStruct '
            {
                "PatientName":              "%_name|patientID_PatientName",
                "PatientID":                "%_md5|7_PatientID",
                "AccessionNumber":          "%_md5|8_AccessionNumber",
                "PatientBirthDate":         "%_strmsk|******01_PatientBirthDate",
                "re:.*hysician":            "%_md5|4_#tag",
                "re:.*stitution":           "#tag",
                "re:.*ddress":              "#tag"
            }
            ' --threads 0 --printElapsedTime

        -- OR equivalently --

        pfdicom_tagSub                                                          \\
            --fileFilter dcm                                                    \\
            --inputDir /var/www/html/normsmall                                  \\
            --outputDir /var/www/html/anon                                      \\
            --splitToken ","                                                    \\
            --splitKeyValue "="                                                 \\
            --tagInfo '
                PatientName         =  %_name|patientID_PatientName,
                PatientID           =  %_md5|7_PatientID,
                AccessionNumber     =  %_md5|8_AccessionNumber,
                PatientBirthDate    =  %_strmsk|******01_PatientBirthDate,
                re:.*hysician       =  %_md5|4_#tag,
                re:.*stitution      =  #tag,
                re:.*ddress         =  #tag
            ' --threads 0 --printElapsedTime

        will replace the explicitly named tags as shown:

        * the ``PatientName`` value will be replaced with a Fake Name,
          seeded on the ``PatientID``;

        * the ``PatientID`` value will be replaced with the first 7 characters
          of an md5 hash of the ``PatientID``;

        * the ``AccessionNumber``  value will be replaced with the first 8
          characters of an md5 hash of the `AccessionNumber`;

        * the ``PatientBirthDate`` value will set the final two characters,
          i.e. the day of birth, to ``01`` and preserve the other birthdate
          values;

        * any tags with the substring ``hysician`` will have their values
          replaced with the first 4 characters of the corresponding tag value
          md5 hash;

        * any tags with ``stitution`` and ``ddress`` substrings in the tag
          contents will have the corresponding value simply set to the tag
          name.

        NOTE:

        Spelling matters! Especially with the substring bulk replace, please
        make sure that the substring has no typos, otherwise the target tags
        will most probably not be processed.

    '''

    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description



parserSelf  = ArgumentParser(description        = str_desc,
                            formatter_class     = RawTextHelpFormatter,
                            add_help            = False)

parserSelf.add_argument("--tagStruct",
                    help    = "JSON formatted tag sub struct",
                    dest    = 'tagStruct',
                    default = '')
parserSelf.add_argument("--tagInfo",
                    help        = "A custom delimited tag sub struct",
                    dest        = 'tagInfo',
                    default     = '')
parserSelf.add_argument("--splitKeyValue",
                    help        = "Expression on which to split the <key><value> pairs",
                    dest        = 'splitKeyValue',
                    default     = ",")
parserSelf.add_argument("--splitToken",
                    help        = "Expression on which to split the <delimited_tag_info>",
                    dest        = 'splitToken',
                    default     = "++")

parser  = ArgumentParser(description        = str_desc,
                         formatter_class    = RawTextHelpFormatter,
                         parents            = [pfdicom_parser, parserSelf],
                         add_help           = False)


def earlyExit_check(args) -> int:
    """Perform some preliminary checks
    """
    if args.man or args.synopsis:
        print(str_desc)
        if args.man:
            str_help     = synopsis(False)
        else:
            str_help     = synopsis(True)
        print(str_help)
        return 1
    if args.b_version:
        print("Name:    %s\nVersion: %s" % (__pkg.name, __version__))
        return 1
    return 0

def main(argv=None):

    d_pfdicom_tagSub    : dict = {}
    args = parser.parse_args()

    if earlyExit_check(args): return 1

    # pudb.set_trace()
    args.str_version        = __version__
    args.str_desc           = synopsis(True)
    pf_dicom_tagSub         = pfdicom_tagSub.pfdicom_tagSub(vars(args))

    # And now run it!
    d_pfdicom_tagSub = pf_dicom_tagSub.run(timerStart = True)

    if args.printElapsedTime:
        pf_dicom_tagSub.dp.qprint(
                                    "Elapsed time = %f seconds" %
                                    d_pfdicom_tagSub['runTime']
                                )

    return 0

if __name__ == "__main__":
    sys.exit(main())
