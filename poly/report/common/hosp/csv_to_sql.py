import sys
import psycopg2
import csv

def csv_to_sql(csv_file, csvClass, test=1, clear=False, logger=None):
     
    #csv_file = input[0] # csv file
    #procClass class instance for transform list to data insert
    #test if > 0 no actually insert print data only

    qonn = psycopg2.connect("dbname=prive user=postgres password=boruh")
    qur = qonn.cursor()
    
    procClass = csvClass(qonn, logger)
    if clear:
        procClass.clear_tbl()
    
    insert = "INSERT INTO public.%s (%s) VALUES (%s)" % \
             (procClass.table, procClass.cols, procClass.vals)
    #print(insert)
    errors = 0
    with open(csv_file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=';', quotechar='"')
        cd = 5
        rc = 0
        wc = 0
        start = True
        for ln in lines:
            if start: # ignore first line
                start = False
                continue
            #data = '%s%s' % (insert, procClass.getData(ln) ) 
            rc += 1
            try:
                data = procClass.getData(ln)
                print('rec %s' % rc, end='\r' )
                if data is None:
                    s = f'None string num {rc}'
                    if logger:
                        logger.debug(s)
                    else:
                        print(s)
                    continue
            except Exception as e:
                if logger:
                    logger.debug(e)
                else:
                    print(e)
            
            if test > 0:
                #rc += 1
                #print (data);
                
                #cd -= 1
                #if cd == 0:
                #    break
                
                #print (' -- rows -- %s' % rc, end="\r" )
                continue
        
            try:
                qur.execute(insert, data)
                qonn.commit()
                wc += qur.rowcount
                #print (' -- rows -- %s' % rc, end="\r" )
            except Exception as e:
                qonn.rollback()
                errors += 1
                if logger:
                    logger.error(e)
    
    qonn.commit()
    qur.close()
    procClass.close()
    qonn.close()
    
    return test, rc, wc, errors
    
    #sys.exit()
    
