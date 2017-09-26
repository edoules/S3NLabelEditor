'''
abiIO.py

I contain the I/O operations on the ABI binary file format specification based on the format docs
released by Life Technologies / Applied Biosystems.

I am different from what's offered by BioEclipse / BioPython / BioPERL etc., because I also read
the raw signals.

These functions are copied-from / based-on an earlier project that mathematically corrupts
raw signals and processed chromatograms, 'abihorrify.py'.
'''

import struct

def skip_header(f):
    header_format = struct.unpack('>4s', f.read(4))[0]
    if header_format != 'ABIF':
        raise Exception("FATAL: The binary file format is not ABIF.")
    version = struct.unpack('>h', f.read(2))[0]
    if version < 100 or version >= 200:
        raise Exception("FATAL: This file is not ABIF version 1.x.")

def grab_directory_entry(f):
    return {
        'name'       :struct.unpack('>4s', f.read(4))[0],
        'number'     :struct.unpack('>i', f.read(4))[0],
        'elementtype':struct.unpack('>h', f.read(2))[0],
        'elementsize':struct.unpack('>h', f.read(2))[0],
        'numelements':struct.unpack('>i', f.read(4))[0],
        'datasize'   :struct.unpack('>i', f.read(4))[0],
        'dataoffset' :struct.unpack('>i', f.read(4))[0],
        'datahandle' :struct.unpack('>i', f.read(4))[0],
    }

def skip_to_record_index(f, record_name, index):
    f.seek(0)
    skip_header(f)
    tdir = grab_directory_entry(f)
    numelements = tdir['numelements']
    dataoffset  = tdir['dataoffset']
    f.seek(dataoffset) # go to the start of the directory list.
    for ielem in xrange(numelements):
        element = grab_directory_entry(f)
        if element['name'] != record_name: continue
        if element['number'] != index: continue
        offset = element['dataoffset']
        length = element['datasize']
        f.seek(offset)
        return length

def file_string_or_handle(filename_or_filehandle):
    locally_opened = False
    try:
        f = open(filename_or_filehandle, 'rb')
        locally_opened = True
    except TypeError:
        f = filename_or_filehandle
    return f, locally_opened

def grab_record_index_type(filename_or_filehandle, record, index, format):
    f, locally_opened = file_string_or_handle(filename_or_filehandle)
    length = skip_to_record_index(f, record, index)
    if not length:
        raise Exception("FATAL: Channel index %d is not valid for record %s." % (index, record))
    format_length = {'h':(length/2),'B':length, 'c':length}[format]
    retval = struct.unpack('>%d%s' % (format_length, format), f.read(length))
    if locally_opened: f.close()
    return retval

def grab_raw_signal(filename_or_filehandle, base):
    index = {'G':1,'A':2,'T':3,'C':4}[base]
    return grab_record_index_type(filename_or_filehandle, 'DATA', index, 'h')

def grab_chromatogram(filename_or_filehandle, base):
    index = {'G':9,'A':10,'T':11,'C':12}[base]
    return grab_record_index_type(filename_or_filehandle, 'DATA', index, 'h')

def grab_pcon(filename_or_filehandle):
    return grab_record_index_type(filename_or_filehandle, 'PCON', 2, 'B')

def grab_ploc(filename_or_filehandle):
    return grab_record_index_type(filename_or_filehandle, 'PLOC', 2, 'h')

def grab_pbas(filename_or_filehandle):
    return ''.join(grab_record_index_type(filename_or_filehandle, 'PBAS', 2, 'c')).upper()

def grab_pcon_user(filename_or_filehandle):
    return grab_record_index_type(filename_or_filehandle, 'PCON', 1, 'B')

def grab_pbas_user(filename_or_filehandle):
    return ''.join(grab_record_index_type(filename_or_filehandle, 'PBAS', 1, 'c')).upper()
