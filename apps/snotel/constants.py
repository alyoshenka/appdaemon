"""Constant variables"""

# pylint: disable=line-too-long
PRE_URL = 'https://wcc.sc.egov.usda.gov/reportGenerator/view/customSingleStationReport/hourly/start_of_period/'
POST_URL = ':MT:SNTL%7Cid=%22%22%7Cname/-167,0/WTEQ::value,SNWD::value,PREC::value,TOBS::value?fitToScreen=false&sortBy=0:-1'

TABLE_ID = 'tabPanel:formReport:tblViewData_data'
HEADER_ID = 'tabPanel:formReport:txtReportTitle'

DATETIME = 'Date Time'
SWE = 'SWE'
DEPTH = 'Depth'
PRECIP = 'Precip'
TEMP = 'Temp'

COLUMNS = [DATETIME, SWE, DEPTH, PRECIP, TEMP]