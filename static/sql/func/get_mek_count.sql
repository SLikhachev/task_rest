CREATE OR REPLACE FUNCTION public.get_mek_count(
    IN _tbl character varying, _month int,

    OUT mecount integer)
  RETURNS integer AS
$BODY$
    begin
        EXECUTE format('SELECT count(tal_num) FROM %s WHERE mek=1 AND talon_month=%s', _tbl, _month)
        INTO mecount;
    END
$BODY$
  LANGUAGE plpgsql VOLATILE

select get_mek_count('talonz_clin_19', 11)