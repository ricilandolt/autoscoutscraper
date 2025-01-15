import os
import psycopg2


POSTGRES_STR = os.getenv("POSTGRES_STR")
if POSTGRES_STR:
    conn = psycopg2.connect(POSTGRES_STR)
else :
    conn = ""

cur = conn.cursor()


# cur.execute("rollback")

sqlstr = """
        SELECT 
            VEH_ID, 
            EXTRACT_DATE,
            VEH_TYPE,
            VEH_DATA -> 'listing' -> 'price' AS price,
            VEH_DATA -> 'listing' -> 'listPrice' AS listPrice,
            VEH_DATA -> 'listing' -> 'bodyColor' AS bodyColor,
            VEH_DATA -> 'listing' -> 'bodyType' AS bodyType,
            VEH_DATA -> 'listing' -> 'cubicCapacity' AS cubicCapacity,
            VEH_DATA -> 'listing' -> 'doors' AS doors,
            VEH_DATA -> 'listing' -> 'driveType' AS driveType,
            VEH_DATA -> 'listing' -> 'firstRegistrationDate' AS firstRegistrationDate,
            VEH_DATA -> 'listing' -> 'fuelType' AS fuelType,
            VEH_DATA -> 'listing' -> 'horsePower' AS horsePower,
            VEH_DATA -> 'listing' -> 'versionFullName' AS versionFullName,
            VEH_DATA -> 'listing' -> 'transmissionType' AS transmissionType,
            VEH_DATA -> 'listing' -> 'mileage' AS mileage,
            VEH_DATA -> 'listing' -> 'id' AS id,
            VEH_DATA -> 'listing' -> 'make' AS make,
            VEH_DATA -> 'listing' -> 'model' AS model,
            VEH_DATA -> 'seller' -> 'name' AS name,
            VEH_DATA -> 'seller' -> 'zipCode' AS zipCode
        FROM autoscout
        where EXTRACT_DATE  > '2025-01-01'::date 
    """
cur.execute(sqlstr)
rs = cur.fetchall()
print(rs)

cur.execute("select veh_type,EXTRACT_DATE, count(*) from autoscout   where EXTRACT_DATE  > '2025-01-01'::date   group by veh_type, EXTRACT_DATE")
rs = cur.fetchall()
print(rs)


cur.execute("select vehtype, startpage, timestamp  from logs ")
rs = cur.fetchall()
print(rs)