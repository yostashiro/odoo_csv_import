'''
Created on 10 sept. 2016

@author: mythrys
'''
import csv
import os

from lib.internal.csv_reader import UnicodeWriter, UnicodeReader


def write_csv(filename, header, data):
    file_result = open(filename, "wb")
    c = UnicodeWriter(file_result, delimiter=';', quoting=csv.QUOTE_ALL)
    c.writerow(header)
    for d in data:
        c.writerow(d)
    file_result.close()

def write_file(filename=None, header=None, data=None, fail=False, model="auto", 
               launchfile="import_auto.sh", worker=1, batch_size=10, init=False, 
               conf_file=False, groupby='', sep=";", python_exe='python', path='./', context=None):
    def get_model():
        if model == "auto":
            return filename.split(os.sep)[-1][:-4]
        else:
            return model

    context = '--context="%s"' % str(context) if context else ''
    conf_file = conf_file or "%s%s%s" % ('conf', os.sep, 'connection.conf')
    write_csv(filename, header, data)

    mode = init and 'w' or 'a'
    with open(launchfile, mode) as myfile:
        myfile.write("%s %sodoo_import_thread.py -c %s --file=%s --model=%s --worker=%s --size=%s --groupby=%s --sep=\"%s\" %s\n" % 
                    (python_exe, path, conf_file, filename, get_model(), worker, batch_size, groupby, sep, context))
        if fail:
            myfile.write("%s %sodoo_import_thread.py -c %s --fail --file=%s --model=%s --sep=\"%s\" %s\n" % 
                         (python_exe, path, conf_file, filename, get_model(), sep, context))


################################################
# Method to merge file together based on a key #
################################################

def write_file_dict(filename, header, data):
    data_rows = []
    for k, val in data.iteritems():
        r = [val.get(h, '') for h in header]
        data_rows.append(r)
    write_csv(filename, header, data_rows)



def read_file_dict(file_name, id_name):
    file_ref = open(file_name, 'r')
    reader = UnicodeReader(file_ref, delimiter=';')

    head = reader.next()
    res = {}
    for line in reader:
        if any(line):
            line_dict = dict(zip(head, line))
            res[line_dict[id_name]] = line_dict
    return res, head

def merge_file(master, child, field):
    res = {}
    for key, val in master.iteritems():
        data = dict(child.get(val[field], {}))
        new_dict = dict(val)
        new_dict.update(data)
        res[key] = new_dict
    return res


def merge_header(*args):
    old_header = [item for sublist in args for item in sublist]
    header = []
    for h in old_header:
        if h and h not in header:
            header.append(h)
    return header
