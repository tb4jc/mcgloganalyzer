'''
Created on 16.02.2016

@author: Thomas
'''
import xlsxwriter

class ExcelWriter(object):
    '''
    classdocs
    '''


    def __init__(self, absFilename):
        '''
        Constructor
        '''
        self.cols = 0
        self.rows = 0
        
        # open new workbook
        self.workbook = xlsxwriter.Workbook(absFilename)

        # Add a worksheet for each autofilter example.
        self.worksheet1 = self.workbook.add_worksheet(name="EventTable")
        
        # Add color formats

    def addHeaders(self, headers):
        self.cols = len(headers)
        
        # Write the headers
        self.worksheet1.write_row('A1', headers)
        self.rows += 1

    def addRow(self, rowData):
        self.worksheet1.write_row(self.rows, 0, rowData)
        if len(rowData) < self.cols:
            self.worksheet1.set_row(self.rows, options={'hidden':True})
        self.rows += 1
        
    def finishFile(self):
        # add formats
        fBold = self.workbook.add_format({'bold':1})
        fTimeStamp = self.workbook.add_format({'num_format':'dd.mm.yyyy hh:mm:ss'})
        
        # add conditional formats
        formatFtpOk = self.workbook.add_format({'bg_color': '#00FF00'})
        formatFtpFail = self.workbook.add_format({'bg_color': '#FF0000'})
        formatGsmDrop = self.workbook.add_format({'bg_color': '#FFC880'})
        formatGsmUp = self.workbook.add_format({'bg_color': '#9EFFCB'})
        formatGsmConnectFailed = self.workbook.add_format({'color':'white',
                                                           'bg_color': '#0038D6'})
        formatGsmReset = self.workbook.add_format({'bg_color': '#DE80FF'})
        self.worksheet1.conditional_format(1, 0, self.rows-1, self.cols-1, {'type':'text',
                                                                            'criteria':'begins with',
                                                                            'value':'FTP OK',
                                                                            'format': formatFtpOk} )
        self.worksheet1.conditional_format(1, 0, self.rows-1, self.cols-1, {'type':'text',
                                                                            'criteria':'begins with',
                                                                            'value':'FTP Failed',
                                                                            'format': formatFtpFail} )
        self.worksheet1.conditional_format(1, 0, self.rows-1, self.cols-1, {'type':'text',
                                                                            'criteria':'begins with',
                                                                            'value':'GSM up',
                                                                            'format': formatGsmUp} )
        self.worksheet1.conditional_format(1, 0, self.rows-1, self.cols-1, {'type':'text',
                                                                            'criteria':'begins with',
                                                                            'value':'GSM drop after',
                                                                            'format':formatGsmDrop})
        self.worksheet1.conditional_format(1, 0, self.rows-1, self.cols-1, {'type':'text',
                                                                            'criteria':'begins with',
                                                                            'value':'GSM connect failed',
                                                                            'format':formatGsmConnectFailed})
        self.worksheet1.conditional_format(1, 0, self.rows-1, self.cols-1, {'type':'text',
                                                                            'criteria':'begins with',
                                                                            'value':'GSM engine reset',
                                                                            'format':formatGsmReset})

        # Make the columns wider and bold
        self.worksheet1.set_row(0, 20, fBold)
        self.worksheet1.set_column(0, self.cols-2, 15, None)
        self.worksheet1.set_column(0, 0, 20, fTimeStamp)
        self.worksheet1.set_column(self.cols-2, self.cols-1, 20, None)

        # Add autofilter and freeze first row
        self.worksheet1.autofilter(first_row=0, first_col=0, last_row=self.rows, last_col=self.cols-1)
        self.worksheet1.filter_column(self.cols-1, 'x == NonBlanks')
        
        self.worksheet1.freeze_panes(1,0)
        self.workbook.close()


if __name__ == '__main__':
    excelWriter = ExcelWriter("C:/workspace/TWCS/___issues/openpyexcel-workbook.xlsx")
    excelWriter.addHeaders(["TIMESTAMP","FIX","NR_SATS","LAT","LONG","SPEED","HEADING","ENG_STATUS","ENG_SIGNAL","ENG_OPERATORNAME","ENG_REGISTRATION","INFO"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2","gsmp connection up"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2","gsmp connection up"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2","GSM up"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2","GSM drop"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2","gsmp connection up"])
    excelWriter.addRow(["09.02.2016 10:39:01","yes","8","48.94995","2.35039","0.01","0.00","3","-51","FSFR","2","jkljk"])
    excelWriter.finishFile()
    
