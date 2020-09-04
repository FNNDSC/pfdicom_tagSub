pfdicom_tagSub
==================

.. image:: https://badge.fury.io/py/pfdicom_tagSub.svg
    :target: https://badge.fury.io/py/pfdicom_tagSub

.. image:: https://travis-ci.org/FNNDSC/pfdicom_tagSub.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/pfdicom_tagSub

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/pfdicom_tagSub

.. contents:: Table of Contents


Quick Overview
--------------

-  ``pfdicom_tagSub`` reads/edits/saves DICOM meta information. It can be used to anonymize DICOM header data.

Overview
--------

``pfdicom_tagSub`` replaces a set of ``<tag, value>`` pairs in a DICOM header with values passed in a JSON structure. Individual DICOM tags can be explicitly referenced in the JSON structure, as well as a regular expression construct to capture all tags satisfying that expression. This allows for capturing all tags with a certain string pattern without needing to explicitly list every confirming tag.

Tag regular expression constructs are ``python`` string expressions and are prefixed by ``"re:<pythonRegex>"``. For example, ``"re:.*hysician"`` will perform some substitution on all tags that contain the letters ``hysician``. The value substitution has access to a special lookup, ``#tag``, which is the current tag hit. It is possible to apply built in functions to the tag hit, for example ``md5`` hashing, using ``"%_md5|4_#tag"``,

.. code:: javascript

    {
        "re:.*hysician":                "%_md5|4_#tag"
    }

will be expanded to

.. code:: javascript

    {
        "PerformingPhysiciansName" :    "%_md5|4_PerformingPhysiciansName"
        "PhysicianofRecord"        :    "%_md5|4_PhysicianofRecord"
        "ReferringPhysiciansName"  :    "%_md5|4_ReferringPhysiciansName"
        "RequestingPhysician"      :    "%_md5|4_RequestingPhysician"
    }

The tag regular expression construct allows for simple and powerful bulk substition of ``<tag, value>`` pairs.

The script accepts an ``<inputDir>``, and then from this point an ``os.walk()`` is performed to extract all the subdirs. Each subdir is examined for DICOM files (in the simplest sense by a file extension mapping) are passed to a processing method that reads and replaces specified DICOM tags, saving the result in a corresponding directory and filename in the output tree.

Installation
------------

Dependencies
~~~~~~~~~~~~

The following dependencies are installed on your host system/python3 virtual env (they will also be automatically installed if pulled from pypi):

-  ``pfmisc`` (various misc modules and classes for the pf* family of objects)
-  ``pftree`` (create a dictionary representation of a filesystem hierarchy)
-  ``pfdicom`` (handle underlying DICOM file reading)

Using ``PyPI``
~~~~~~~~~~~~~~

The best method of installing this script and all of its dependencies is
by fetching it from PyPI

.. code:: bash

        pip3 install pfdicom_tagSub

Command line arguments
----------------------

.. code:: html


        -I|--inputDir <inputDir>
        Input DICOM directory to examine. By default, the first file in this
        directory is examined for its tag information. There is an implicit
        assumption that each <inputDir> contains a single DICOM series.

        -i|--inputFile <inputFile>
        An optional <inputFile> specified relative to the <inputDir>. If
        specified, then do not perform a directory walk, but convert only
        this file.

        -e|--extension <DICOMextension>
        An optional extension to filter the DICOM files of interest from the
        <inputDir>.

        [-O|--outputDir <outputDir>]
        The output root directory that will contain a tree structure identical
        to the input directory, and each "leaf" node will contain the analysis
        results.

        -F|--tagFile <JSONtagFile>
        Parse the tags and their "subs" from a JSON formatted <JSONtagFile>.

        -T|--tagStruct <JSONtagStructure>
        Parse the tags and their "subs" from a JSON formatted <JSONtagStucture>
        passed directly in the command line.

        -o|--outputFileStem <outputFileStem>
        The output file stem to store data. This should *not* have a file
        extension, or rather, any "." in the name are considered part of
        the stem and are *not* considered extensions.

        [--outputLeafDir <outputLeafDirFormat>]
        If specified, will apply the <outputLeafDirFormat> to the output
        directories containing data. This is useful to blanket describe
        final output directories with some descriptive text, such as
        'anon' or 'preview'.

        This is a formatting spec, so

            --outputLeafDir 'preview-%s'

        where %s is the original leaf directory node, will prefix each
        final directory containing output with the text 'preview-' which
        can be useful in describing some features of the output set.

        [--threads <numThreads>]
        If specified, break the innermost analysis loop into <numThreads>
        threads.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

        [--json]
        If specified, output a JSON dump of final return.

        [--followLinks]
        If specified, follow symbolic links.

        -v|--verbosity <level>
        Set the app verbosity level.

            0: No internal output;
            1: Run start / stop output notification;
            2: As with level '1' but with simpleProgress bar in 'pftree';
            3: As with level '2' but with list of input dirs/files in 'pftree';
            5: As with level '3' but with explicit file logging for
                    - read
                    - analyze
                    - write

Examples
--------

Perform a DICOM anonymization by processing specific tags:

.. code:: bash

        pfdicom_tagSub                                      \
            -e dcm                                          \
            -I /var/www/html/normsmall                      \
            -O /var/www/html/anon                           \
            --tagStruct '
            {
                "PatientName":              "%_name|patientID_PatientName",
                "PatientID":                "%_md5|7_PatientID",
                "AccessionNumber":          "%_md5|8_AccessionNumber",
                "PatientBirthDate":         "%_strmsk|******01_PatientBirthDate",
                "re:.*hysician":            "%_md5|4_#tag"
                "re:.*stitution":           "#tag",
                "re:.*ddress":              "#tag"
            }
            ' --threads 0 --printElapsedTime

will replace the explicitly named tags as shown:

* the ``PatientName`` value will be replaced with a Fake Name, seeded on the ``PatientID``;

* the ``PatientID`` value will be replaced with the first 7 characters of an md5 hash of the ``PatientID``;

* the ``AccessionNumber``  value will be replaced with the first 8 characters of an md5 hash of the `AccessionNumber`;

* the ``PatientBirthDate`` value will set the final two characters,i.e. the day of birth, to ``01`` and preserve the other birthdate values;

* any tags with the substring ``hysician`` will have their values replaced with the first 4 characters of the corresponding tag value md5 hash;

* any tags with ``stitution`` and ``ddress`` substrings in the tag contents will have the corresponding value simply set to the tag name.

NOTE:

Spelling matters! Especially with the substring bulk replace, please make sure that the substring has no typos, otherwise the target tags will most probably not be processed.

_-30-_
