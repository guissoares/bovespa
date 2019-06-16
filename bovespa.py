# -*- coding: utf-8 -*-

import os.path
import glob
import datetime
import numpy as np
import logging

stock_quote_dtype = np.dtype([
    ('date', 'U8'),
    ('codbdi', 'u1'),
    ('codneg', 'U12'),
    ('tpmerc', 'u2'),
    ('nomres', 'U12'),
    ('especi', 'U10'),
    ('prazot', 'u2'),
    ('modref', 'U4'),
    ('preabe', 'i8'),
    ('premax', 'i8'),
    ('premin', 'i8'),
    ('premed', 'i8'),
    ('preult', 'i8'),
    ('preofc', 'i8'),
    ('preofv', 'i8'),
    ('totneg', 'u4'),
    ('quatot', 'u8'),
    ('voltot', 'i8'),
    ('preexe', 'i8'),
    ('indopc', 'u1'),
    ('datven', 'U8'),
    ('fatcot', 'u4'),
    ('ptoexe', 'i8'),
    ('codisi', 'U12'),
    ('dismes', 'u2')
])

class YearData(object):

    def __init__(self, filepath=None):
        if filepath:
            self.parse_file(filepath)

    def _parse_date(self, date_string):
        return datetime.datetime.strptime(date_string, '%Y%m%d').date()

    def _parse_number(self, number_string, dtype, default=None):
        try:
            return np.array(number_string, dtype=dtype)
        except ValueError:
            return default

    def _parse_header(self, line):
        reg_type = line[0:2]
        filename = line[2:15]
        origcode = line[15:23].strip()
        filedate = line[23:31]
        assert reg_type == '00', reg_type
        assert origcode.upper() == 'BOVESPA', origcode
        self.filename = filename
        self.date = self._parse_date(filedate)

    def _parse_trailer(self, line):
        reg_type = line[0:2]
        filename = line[2:15]
        origcode = line[15:23].strip()
        filedate = line[23:31]
        assert reg_type == '99'
        assert origcode.upper() == 'BOVESPA', origcode
        assert filename == self.filename
        assert self._parse_date(filedate) == self.date

    def _parse_line(self, line):
        reg_type = line[0:2]
        assert reg_type == '01'
        stock_quote = np.array((
            line[2:10],             # date
            line[10:12],            # codbdi
            line[12:24].strip(),    # codneg
            line[24:27],            # tpmerc
            line[27:39].strip(),    # nomres
            line[39:49].strip(),    # especi
            self._parse_number(line[49:52], 'u2', 0),   # prazot
            line[52:56].strip(),    # modref
            line[56:69],            # preabe
            line[69:82],            # premax
            line[82:95],            # premin
            line[95:108],           # premed
            line[108:121],          # preult
            line[121:134],          # preofc
            line[134:147],          # preofv
            line[147:152],          # totneg
            line[152:170],          # quatot
            line[170:188],          # voltot
            line[188:201],          # preexe
            line[201:202],          # indopc
            line[202:210].strip(),  # datven
            line[210:217],          # fatcot
            line[217:230],          # ptoexe
            line[230:242].strip(),  # codisi
            line[242:245]           # dismes
        ), dtype=stock_quote_dtype)
        return stock_quote

    def parse_file(self, filepath):
        with open(filepath, 'r', encoding='ISO-8859-1') as fp:
            lines = fp.readlines()
            self._parse_header(lines[0])
            self._parse_trailer(lines[-1])
            size = len(lines)-2
            self.data = np.zeros(size, dtype=stock_quote_dtype)
            for i, line in enumerate(lines[1:-1]):
                self.data[i] = self._parse_line(line)


class BovespaData(object):

    def __init__(self, data_path=None):
        if data_path:
            self.read_data(data_path)

    def read_data(self, data_path):
        filepaths = glob.glob(os.path.join(data_path, 'COTAHIST*'))
        year_data = []
        for filepath in filepaths:
            logging.info('Lendo arquivo {}...'.format(filepath))
            year_data.append(YearData(filepath))
        year_data = sorted(year_data, key=lambda x: x.date)
        year_data_arrays = [yd.data for yd in year_data]
        self.data = np.concatenate(year_data_arrays)
