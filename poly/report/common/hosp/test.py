import sys
from csv_to_sql import csv_to_sql
from hosp_class import HospEir

# hosp_csv F:\ports\pavlenkov\fond\new\LPU_PK.csv 1
   
if __name__ == "__main__":
    input = sys.argv[1:]
    if input == []:
        print ("No input")
        sys.exit()        
    csv_file = input[0] # csv file
    test = input[1] # no actually insert print data only
    tst = int(test)
    ts, rc, wc, errors = csv_to_sql(csv_file, HospEir, tst, clear=True)
    print (f'test: {ts}, read: {rc}, write: {wc}, errors: {errors}')
    
