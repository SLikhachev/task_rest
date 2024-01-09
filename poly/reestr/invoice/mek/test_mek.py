
import psycopg2
import psycopg2.extras

table_exists ='''
SELECT EXISTS (
    SELECT FROM
        pg_tables
    WHERE
        schemaname = 'public' AND
        tablename  = '{}'
    );
'''

select_keys = '''
SELECT * FROM {} LIMIT 1;
'''

# to prevent double insert we use talon_type=1
# after insert we set this flag to 2 (closed talon)
# then we need to update this flag to 1 manually if we need
# insert ones time again
insert_mek='''
INSERT INTO {to_table} ({fields})
    SELECT {fields} FROM {from_table} as t
    WHERE t.mek=1 AND t.talon_month=12 AND t.talon_type=1
    ORDER BY tal_num
    RETURNING tal_num;
'''

update_month='''
UPDATE {to_table} SET talon_month=1
WHERE talon_month=12 AND mek=1;
'''

select_tal_nums = '''
SELECT tal_num FROM {table}
WHERE talon_month=12 and mek=1 ORDER BY tal_num;
'''

update_type='''
UPDATE {table} SET talon_type=2 WHERE tal_num={tal_num};
'''

insert_pmu='''
INSERT INTO {to_pmu} ({pmu_fields}) VALUES (
'{tal_num}', '{date_usl}', '{code_usl}', '{kol_usl}',
'{exec_spec}', '{exec_doc}', '{exec_podr}'
);
'''
select_pmu = '''
SELECT * FROM {from_pmu} as t
WHERE t.tal_num={tal_num};
'''

pmu_fields="tal_num, date_usl, code_usl, kol_usl, exec_spec, exec_doc, exec_podr"


def test(from_year, to_year):

    db = psycopg2.connect("postgres://postgres:boruh@192.168.0.31:5432/hokuto?sslmode=disable")
    qurs = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    talonz, pmu  = 'talonz_clin', 'para_clin'
    from_table = f'{talonz}_{from_year}'
    to_table = f'{talonz}_{to_year}'
    from_pmu = f'{pmu}_{from_year}'
    to_pmu = f'{pmu}_{to_year}'

    # check the the tables exists
    for table in (to_table, to_pmu):
        qurs.execute(table_exists.format(table))
        res=qurs.fetchone()
        if not res.exists:
            print(f"Table {table} not exists")
            return #(abort)

    # select keys from table
    qurs.execute(select_keys.format(from_table))
    res=qurs.fetchone()

    # construct query
    fields = ",".join(list(res._fields)[1:])
    q = insert_mek.format(from_table=from_table, to_table=to_table, fields=fields)
    #print(q)
    # execute insert talonz
    qurs.execute(q)
    db.commit()
    res_insert=qurs.fetchall()
    # should retun iserted tal_nums
    if len(res_insert) == 0:
        print("Nothing to move meks")
        return

    # insert pmu from old to new table
    # select tal_nums from old talonz table
    qurs.execute(select_tal_nums.format(table=from_table))
    idx=0
    for tal_from in qurs.fetchall():
        tal_num_from = tal_from.tal_num
        # should be same records with differnt tal_nums from old and new tables
        tal_num_to = res_insert[idx].tal_num
        print(tal_num_from, tal_num_to)
        # then fetch all pmu with that tal_num (from old table)
        qurs.execute(select_pmu.format(from_pmu=from_pmu, tal_num=tal_num_from))
        pmus = qurs.fetchall()
        if len(pmus) == 0:
            print(f"Error: not found pmu for talon {tal_num_from}")

        # then insert all fetched to the new table with new tal_num ref
        for pmu in qurs.fetchall():
            q = insert_pmu.format(
                to_pmu=to_pmu, pmu_fields=pmu_fields,
                tal_num=tal_num_to, date_usl=pmu.date_usl, code_usl=pmu.code_usl,
                kol_usl=pmu.kol_usl, exec_spec=pmu.exec_spec,
                exec_doc=pmu.exec_doc, exec_podr=pmu.exec_podr
            )
            print(q)
            qurs.execute(q)

        # update type in old table to prevent maybe second moving
        qurs.execute(update_type.format(table=from_table, tal_num=tal_num_from))

        # commit trans and increase index
        db.commit()
        idx += 1

    # and finally update month in target table
    qurs.execute(update_month.format(to_table=to_table))
    db.commit()


test(23, 24)