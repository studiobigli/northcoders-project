from src.connection import db_connection
from src.utils import (
    get_all_rows,
    get_columns,
    write_to_s3,
    get_tables,
    read_timestamp_from_s3,
    get_new_rows,
    write_df_to_csv,
    table_to_dataframe,
    timestamp_from_df,
    write_timestamp_to_s3,
)
from datetime import datetime
import json
import logging
import boto3

logger = logging.getLogger()


def lambda_handler(event, context):
    try:
        conn = db_connection()
        s3 = boto3.client("s3")
        for table in get_tables(conn):
            timestamp_from_df = read_timestamp_from_s3(s3, table)
            if timestamp_from_df == {"detail" : "No timestamp exists"}:
                rows = get_all_rows(conn, table)
            else:
                rows = get_new_rows(conn, table, timestamp_from_df)
            columns = get_columns(conn, table)

            if rows != []:
                df = table_to_dataframe(rows, columns)
                write_df_to_csv(s3, df, table)
                write_timestamp_to_s3(s3, df, table)
            else:
                logging.info(f"No new data in table {table} to upload.")
   
        logger.error("Houston, we have a %s", "major problem", exc_info=True)
        return {"response": 200}

    except Exception as e:
        logging.error(e)
        return {"response": 500, "error": e}
