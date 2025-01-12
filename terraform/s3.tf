## S3 bucket to store lambda code
resource "aws_s3_bucket" "code_bucket" {
    bucket = "nc-terraformers-code"
    tags = {
        name = "code_bucket"
        environment = "dev"
        description = "S3 bucket to store and provide lambda_handler code for lambda1."
    }
}

## Ingestion S3 bucket
resource "aws_s3_bucket" "ingestion_bucket" {
    bucket = "nc-terraformers-ingestion"
    tags = {
        name = "ingestion_bucket"
        environment = "dev"
        description = "S3 bucket to store extracted raw tables from ToteSys."
    }
}

## Processing S3 bucket
resource "aws_s3_bucket" "processing_bucket" {
    bucket = "nc-terraformers-processing"
    tags = {
        name = "processing_bucket"
        environment = "dev"
        description = "S3 bucket to store processed tables from Lambda2."
    }
}

## zip file for numpy/fastparquet layer in S3 code bucket
resource "aws_s3_object" "overwrite_awslayer" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "overwrite_awslayer.zip"
  source = var.overwrite_awslayer_file
  etag   = filemd5(var.overwrite_awslayer_file)
  depends_on = [ var.overwrite_awslayer_file ]
}