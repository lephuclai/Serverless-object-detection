import subprocess
import xlsxwriter
from time import sleep
workbook = xlsxwriter.Workbook('Example2.xlsx')
worksheet = workbook.add_worksheet()

column = 0
for x in range(5):
    row = 0
    address = 'http://serverless.default.172.16.42.90.sslip.io/api/stream/192.168.1.2:1935/15'
    command = 'curl -w @curl-format.txt -o /dev/null -s '+ address
    time_namelookup = subprocess.getoutput(command)
    result = list(time_namelookup.split(" "))
    
    # iterating through content list
    for item in result :
    
        # write operation perform
        worksheet.write(row, column, item)
    
        # incrementing the value of row by one
        # with each iterations.
        row += 1
        
    
    column += 1
    sleep(45)
workbook.close()



