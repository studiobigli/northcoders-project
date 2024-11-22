import pandas as pd

from src.week3_lambda import lambda_handler
from src.lambda3_utils import import_pq_to_df, df_to_sql
from testfixtures import LogCapture
import pytest

@pytest.fixture(scope="function")
def refresh_dim_staff(conn_fixture):
    conn_fixture.run("DELETE FROM dim_staff;")

class TestGetParquet:
    def test_returns_dataframe(self, nc_terraformers_processing_s3):
        output = import_pq_to_df(nc_terraformers_processing_s3, "test_staff.parquet")
        assert isinstance(output, pd.DataFrame)

    def test_df_unchanged(self, nc_terraformers_processing_s3, test_dim_df):
        output = import_pq_to_df(nc_terraformers_processing_s3, "test_staff.parquet")
        assert output.equals(test_dim_df)

    def test_handles_no_such_key_error(self, nc_terraformers_processing_s3):
        with LogCapture() as l:
            output = import_pq_to_df(
                nc_terraformers_processing_s3, "invalid_file.parquet"
            )
            assert output == {"result": "failure"}
            assert (
                "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist."
                in str(l)
            )

    def test_logs_progress(self, nc_terraformers_processing_s3):
        with LogCapture() as l:
            import_pq_to_df(nc_terraformers_processing_s3, "test_staff.parquet")
            assert (
                "Reading test_staff.parquet from nc-terraformers-processing bucket"
                in str(l)
            )
            assert (
                "test_staff.parquet file successfully imported into DataFrame" in str(l)
            )


class TestDataFrameToSQL:
    def test_returns_int_of_inserted_rows(self, test_dim_df, conn_fixture, refresh_dim_staff):
        output = df_to_sql(test_dim_df, "dim_staff", conn_fixture)
        assert output == 3

    def test_df_data_written_to_db(self, test_dim_df, conn_fixture, refresh_dim_staff):
        output = df_to_sql(test_dim_df, "dim_staff", conn_fixture)
        dim_staff = conn_fixture.run("SELECT * FROM dim_staff")
        columns = [col['name'] for col in conn_fixture.columns]
        assert len(dim_staff) == output
        assert columns == list(test_dim_df.columns)

    def test_logs_progress(self, test_dim_df, conn_fixture, refresh_dim_staff):
        with LogCapture() as l:
            df_to_sql(test_dim_df, "dim_staff", conn_fixture)
            assert "Inserting values into dim_staff" in str(l)
            assert "3 rows inserted into dim_staff successfully" in str(l)

    def test_handles_table_name_error(self, test_dim_df, conn_fixture, refresh_dim_staff):
        with LogCapture() as l:
            output = df_to_sql(test_dim_df, "invalid_table", conn_fixture)
            assert """relation "invalid_table" does not exist""" in str(l)
            assert output == None

    def test_handles_df_sql_columns_mismatch(self, test_dim_df, conn_fixture):
        with LogCapture() as l:
            output = df_to_sql(test_dim_df, "fact_sales_order", conn_fixture)
            assert """'column "staff_id" of relation "fact_sales_order" does not exist""" in str(l)
            assert output == None

    def test_handles_empty_df(self, conn_fixture):
        with LogCapture() as l:
            output = df_to_sql(pd.DataFrame(), "dim_staff", conn_fixture)
            assert output == None
            assert "Malformed DataFrame: Empty DataFrame" in str(l)
