# Utility functions to validate a csv structure of a file
import csv

import csvvalidator as cv #csvvalidator library
import magic #python-magic library

def write_problems(problems, file, summarize=False, limit=0):
    """
    Write problems as restructured text to a file (or stdout/stderr). Function, taken from csvvalidator library and
    modified for Python 3 compatability
    Args:
        problems (list): list of dictionary objects returned from CSVValidator.validate
        file (object): to write report to (or stdout/stderr)
        summarize (boolean): flag to indicate whether to only write the report summary
        limit (int): lists maximum number of problems in the report
    Returns:
        integer: The total number of problems found
    """
    w = file.write # convenience variable
    w("""
=================
Validation Report
=================
""")
    counts = dict() # store problem counts per problem code
    total = 0
    for i, p in enumerate(problems):
        if limit and i >= limit:
            break # bail out
        if total == 0 and not summarize:
            w("""
Problems
========
""")
        total += 1
        code = p['code']
        if code in counts:
            counts[code] += 1
        else:
            counts[code] = 1
        if not summarize:
            ptitle = '\n%s - %s\n' % (p['code'], p['message'])
            w(ptitle)
            underline = ''
            for i in range(len(ptitle.strip())):
                underline += '-'
            underline += '\n'
            w(underline)
            for k in sorted(p.keys() - set(['code', 'message', 'context'])):
                w(':%s: %s\n' % (k, p[k]))
            if 'context' in p:
                c = p['context']
                for k in sorted(c.keys()):
                    w(':%s: %s\n' % (k, c[k]))

    w("""
Summary
=======
Found %s%s problem%s in total.
""" % ('at least ' if limit else '', total, 's' if total != 1 else ''))
    for code in sorted(counts.keys()):
        w(':%s: %s\n' % (code, counts[code]))
    return total

def validate_csv_file(data_path,report_path,validator):

    # Validate CSV structure
    with open(data_path,"r") as fin:
        data = csv.reader(fin)

    problems = validator.valiate(data)

    if len(problems) == 0:
        print("""There are structural issues with the incoming CSV file. Look into the report: {:s} for more
            information""".format(report_path))

        with open(report_path,"w") as fout:
            write_problems(problems,fout)
        return True

    return False

def sampleValidation():
    """
        Sample code to validate a CSV file structure
    """
    data_path = "data.csv"
    report_path = "csv_validation_problems_report.txt"

    field_names = ('date','','','type','reach','clicks','reactions')
    validator = cv.CSVValidator(field_names)

    validator.add_value_check('date',cv.datetime_string('%m/%d/%Y'),'EX1','invalid date')
    validator.add_value_check('type',cv.enumeration('Video','Photo','Link'),"EX2","invalid type found")
    validator.add_value_check('reach',int,"EX3","reach should be an integer")
    validator.add_value_check('clicks',int,"EX4","clicks should be an integer")
    validator.add_value_check('reactions',int,"EX4","reactions should be an integer")

    validate_csv_file(data_path,report_path,validator)
