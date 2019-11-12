import sys
import csv

def csv_to_sql(app, csv_file, csvClass, test=1, clear=False):
     
    #csv_file = csv file
    #procClass class instance for transform list to data insert
    #test if > 0 no actually insert print data only

    qonn = app.config.db()
    qurs = qonn.cursor()
    
    procClass = csvClass(qonn, app.logger)
    if clear:
        procClass.clear_tbl()
    
    insert = "INSERT INTO public.%s (%s) VALUES (%s)" % \
             (procClass.table, procClass.cols, procClass.vals)
    #print(insert)
    errors = 0
    with open(csv_file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=';', quotechar='"')
        rc = 0
        wc = 0
        start = True
        for ln in lines:
            if start: # ignore first line
                start = False
                continue
            rc += 1
            try:
                data = procClass.getData(ln)
                if data is None:
                    app.logger.debug(f'Error in CSV line num {rc}')
                    errors += 1
                    continue
                if test > 0:
                    continue
                qurs.execute(insert, data)
                wc += qur.rowcount
            except Exception as e:
                app.logger.debug('Exception in csv line %s', rc)
                raise e
    
    qonn.commit()
    qurs.close()
    procClass.close()
    qonn.close()
    
    return test, rc, wc, errors
    
    #sys.exit()
    
