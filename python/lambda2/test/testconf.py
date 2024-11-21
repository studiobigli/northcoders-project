from moto import mock_aws
import boto3
import pytest
import os
import pandas as pd
from io import BytesIO

@pytest.fixture(scope="function")
def aws_cred():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

@pytest.fixture(scope="function")
def processing_bucket():
    with mock_aws():
        s3 = boto3.client("s3")
        test_bucket = "nc-terraformers-processing"
        s3.create_bucket(
            Bucket=test_bucket,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield s3

@pytest.fixture(scope="function")
def ingestion_bucket():
    with mock_aws():
        s3 = boto3.client("s3")
        test_bucket = "nc-terraformers-ingestion"
        s3.create_bucket(
            Bucket=test_bucket,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3.upload_file("test/design_timestamp.json",
                                      "nc-terraformers-ingestion",
                                      "design_timestamp.json")
        s3.upload_file("test/design_timestamp.json",
                                      "nc-terraformers-ingestion",
                                      "staff_timestamp.json")
        s3.upload_file(
            "test/design_2024-11-18 10_56_09.970000.csv",
             "nc-terraformers-ingestion",
             "design/design_2024-11-18 10:56:09.970000.csv")
        s3.upload_file(
            "test/design_2024-11-18 16_47_28.291856.csv",
             "nc-terraformers-ingestion",
             "design/design_2024-11-18 16_47_28.291856.csv")
        s3.upload_file(
            "test/design_2024-11-18 19_15_01.821957.csv",
             "nc-terraformers-ingestion",
             "design/design_2024-11-18 19_15_01.821957.csv")
        s3.upload_file(
            "test/staff_2024-11-18 16_53_23.353536.csv",
             "nc-terraformers-ingestion",
             "staff/staff_2024-11-18 19_15_01.821957.csv")
        yield s3

@pytest.fixture(scope="function")
def test_parquet():
    data = [['a1', 'b1'], ['a2', 'b2'], ['a3', 'b3']]
    input_df = pd.DataFrame(data, columns=['col1', 'col2'])
    out_buffer = BytesIO()
    input_df.to_parquet(out_buffer, index=False)
    yield out_buffer