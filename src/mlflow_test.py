# import findspark

# findspark.init()

import os
from loguru import logger
from functools import partial
from argparse import ArgumentParser
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.types import IntegerType,LongType,DoubleType,StringType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.functions import vector_to_array
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import types as T
from pyspark.sql.types import IntegerType,LongType,DoubleType,StringType,ArrayType
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, SparkTrials, Trials
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import mlflow.spark
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository
#import numpy as np


def main():


    spark = SparkSession\
        .builder\
        .appName('Spark ML Research')\
        .getOrCreate()

    mlflow.set_experiment('classification')

    data = spark.createDataFrame([
        (0.0, 1.0, 0.0),
        (1.0, 0.0, 1.0),
        (2.0, 1.0, 0.0),
        (3.0, 1.0, 1.0)
    ], ["label", "feature1", "feature2"])

    assembler = VectorAssembler(inputCols=["feature1", "feature2"], outputCol="features")
    training_data = assembler.transform(data)
    lr = LogisticRegression(maxIter=10)
    model = lr.fit(training_data)

    MODEL_NAME_MLFLOW = "fraud-detection_v1"

    with mlflow.start_run() as run:
        mlflow.log_metric("shape",training_data.count())
        mlflow.log_param("maxIter", lr.getMaxIter())
        #mlflow.log_metric("training_accuracy", model.summary.accuracy)

        mlflow.spark.log_model(model, artifact_path="models", registered_model_name=MODEL_NAME_MLFLOW)
        #mlflow.spark.log_model(model, "model")
    
        mlflow.end_run()

    




if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--mlflow", required=True, help="Mlflow uri")
    parser.add_argument("--aws_acc", required=True, help="AWS accses key")
    parser.add_argument("--aws_sec", required=True, help="AWS secret key")
    args = parser.parse_args()
    bucket_name = args.bucket
    mlflow_ip = args.mlflow
    aws_acc = args.aws_acc
    aws_sec = args.aws_sec

    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://storage.yandexcloud.net'
    os.environ['MLFLOW_TRACKING_URI'] = f'http://{mlflow_ip}:8000'
    os.environ["AWS_ACCESS_KEY_ID"] = f'{aws_acc}'
    os.environ["AWS_SECRET_ACCESS_KEY"] = f'{aws_sec}'

    main()
