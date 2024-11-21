import pandas as pd

from src.week3_lambda import lambda_handler
from src.lambda3_utils import import_pq_to_df, df_to_sql
from testfixtures import LogCapture


class TestGetParquet:
    def test_returns_dataframe(self, nc_terraformers_processing_s3):
        output = import_pq_to_df(nc_terraformers_processing_s3, "test_staff.parquet")
        assert isinstance(output, pd.DataFrame)

    def test_df_unchanged(self, nc_terraformers_processing_s3, test_df):
        output = import_pq_to_df(nc_terraformers_processing_s3, "test_staff.parquet")
        assert output.equals(test_df)

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
    # def test_df_to_sql_returns_int(self, conn_fixture):
    #     assert df_to_sql() == 1
    assert 1 == 1