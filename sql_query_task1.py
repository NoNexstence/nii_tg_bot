raw_query = """
        WITH calculated_data AS (
            SELECT
                s.year,
                s.region,
                s.tip_mo,
                ROUND(
                CAST(REPLACE(s.value, ',', '.') AS FLOAT) * 100.0 / 
                SUM(CAST(REPLACE(s.value, ',', '.') AS FLOAT)) 
                OVER (PARTITION BY s.year, s.region), 2) as org_percentage

            FROM StatInfo AS s
            WHERE s.name_value = 'Число организаций, ед'
        ),
        visits_data AS (
            SELECT
                si.year,
                si.region,
                si.tip_mo,
                ROUND((CAST(REPLACE(si.value, ',', '.') AS FLOAT) / p.population * 100000), 2) as visits_per_100k
            FROM StatInfo si
            JOIN Population p ON si.region = p.region AND si.year = p.year
            WHERE name_value = 'Число посещений к врачам, включая профилактические (без посещений к стоматологам и зубным врачам), ед'
        )

        SELECT
            cd.year,
            cd.region,
            cd.tip_mo,
            cd.org_percentage,
            RANK() OVER (PARTITION BY cd.year, cd.region ORDER BY cd.org_percentage DESC) as rank_org,
            vd.visits_per_100k,
            RANK() OVER (PARTITION BY cd.year, cd.region ORDER BY vd.visits_per_100k ASC) as rank_visits
        FROM calculated_data cd
        JOIN visits_data vd ON cd.year = vd.year AND cd.region = vd.region AND cd.tip_mo = vd.tip_mo
    """