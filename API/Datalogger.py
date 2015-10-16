# Copyright (C) 2014 Rémi Bèges
# For conditions of distribution and use, see copyright notice in the LICENSE file

import os
import numpy as np
import xlsxwriter
from operator import itemgetter
import time
import logging
import string
import re
import os.path

class Datalogger:
    def __init__(self):
        # Storage for emergency data
        self.data = dict()
        self.startrow = 1
        self.startcolumn = 1

    def append(self,dataid,datatime,dataindex,datavalue):
        # Create table if not existing
        if not dataid in self.data:
            self.data[dataid] = list()

        self.data[dataid].append((datatime,dataindex,datavalue))

    def export(self):
        if not self.data:
            return

        # Create subfolder in log
        basefolder = r'Log/'
        if not os.path.exists(basefolder):
            os.mkdir(basefolder)

        filepath = basefolder + r'/log_' + time.strftime("%Y_%m_%d_%H-%M-%S") + ".xlsx"
        # Avoid erasing a previous file. Mostly used for automated tests.
        inc = 2
        while os.path.isfile(filepath):
            filepath = basefolder + r'/log_' + time.strftime("%Y_%m_%d_%H-%M-%S") + "__" + str(inc) + "__.xlsx"
            inc += 1

        workbook = xlsxwriter.Workbook(filepath)

        for key in self.data:
            # Remove unallowed characters for sheet name
            allow = string.ascii_letters + string.digits + '-'
            protectedkey = re.sub('[^%s]' % allow, '_', key)

            # Create sheet
            worksheet = workbook.add_worksheet(protectedkey)

            # Sort table by time
            self.data[key].sort(key=itemgetter(0))

            # Write headers
            worksheet.write(self.startrow,self.startcolumn,"Time")
            worksheet.write(self.startrow-1,self.startcolumn+1,"Indexes")

            timepoints = dict()
            maxindex = 0

            currentrow = self.startrow + 1

            # For each point in the array
            for (x,y,z) in self.data[key]:
                if not x in timepoints:
                    timepoints[x] = currentrow
                    currentrow += 1
                    # Write time on first column
                    worksheet.write(timepoints[x],self.startcolumn,x)

                if y > maxindex:
                    maxindex = y

                # Write value z at row for given timepoint and column for corresponding index
                worksheet.write(timepoints[x],self.startcolumn + y + 1,z)

            # Write index numbers
            for i in range(maxindex+1):
                worksheet.write(self.startrow,self.startcolumn + i + 1,i)

            # TODO : If number of indexes is 1, add the graph data versus time
            # TODO : If number of indexes > 1, add the graph data versus index for the first time point

        workbook.close()
        logging.info("Wrote data to "+filepath)
        self.data = dict()
