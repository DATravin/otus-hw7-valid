import findspark

findspark.init()

import os
from loguru import logger
from functools import partialS
from argparse import ArgumentParser
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.types import IntegerType,LongType,DoubleType,StringType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.functions import vector_to_array
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import types as T
from pyspark.sql.types import IntegerType,LongType,DoubleType,StringType,ArrayType
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, SparkTrials, Trials
#import mlflow
import pandas as pd

numericColumnsFinal =['term_amount_min',
         'term_amount_50perc',
         'term_amount_max',
         'tx_amount',
         'term_avg_amount_in_day_7d',
         'sh_bad_trans_per_cust',
         'cust_cnt_in_day_7d',
         'rel_cust_50perc',
         'sh_bad_days_per_term',
         'rel_cust_amount_to_max']

featureColumns = numericColumnsFinal

def datamart(date_list,row,agg_cust,agg_term,list_for_fillna,sample_val):

    eps = 1e-6

    df = (row
               .filter(F.col('date_key').isin(date_list))
               .join(agg_term, on=['terminal_id','date_key'], how='left')
               .join(agg_cust, on=['customer_id','date_key'], how='left')
               .fillna(value=0,subset=list_for_fillna)
               #.withColumn("sh_bad_trans_per_cust", sdf['cust_bad_cnt_trans_7d'] / (sdf.cust_total_cnt_trans_7d + eps))
    #            .withColumn("sh_bad_trans_per_term", sdf.term_bad_cnt_trans_7d / (sdf.term_total_cnt_trans_7d + eps))
              )

    #sdf.printSchema()

    df = (df


               .withColumn("sh_bad_trans_per_cust", df['cust_bad_cnt_trans_7d'] / (df['cust_total_cnt_trans_7d'] + eps))
               .withColumn("sh_bad_trans_per_term", df['term_bad_cnt_trans_7d'] / (df['term_total_cnt_trans_7d'] + eps))
               .withColumn("sh_bad_days_per_cust", df['cust_days_with_bad_trans_7d'] / (df['cust_active_days_7d'] + eps))
               .withColumn("sh_bad_days_per_term", df['term_days_with_bad_trans_7d'] / (df['term_active_days_7d'] + eps))
               .withColumn("sh_bad_trans_per_cust", df['cust_bad_cnt_trans_7d'] / (df['cust_total_cnt_trans_7d'] + eps))
               .withColumn("rel_cust_amount_to_max", (df['tx_amount']-df['cust_amount_min'])\
                           / (df['cust_amount_max'] - df['cust_amount_min'] + eps))
               .withColumn("rel_term_amount_to_max", (df['tx_amount']-df['term_amount_min'])\
                           / (df['term_amount_max'] - df['term_amount_min'] + eps))
               .withColumnRenamed('tx_fraud', 'target')

               )
    if sample_val<1 and sample_val>0:
        df = df.sample(sample_val)

    #train_sdf.printSchema()
    return df


# Определяем пространство поиска для hyperopt
search_space = {
    'numTrees': hp.randint('numTrees', 50, 150),
    'maxDepth': hp.randint('maxDepth', 3,7)
}


def objective(params, train_data, test_data):
    logger.info(f"params {params}")


    assembler = VectorAssembler()\
    .setInputCols(featureColumns)\
    .setOutputCol("features")

    scaler = MinMaxScaler()\
        .setInputCol("features")\
        .setOutputCol("scaledFeatures")

    rf = RandomForestClassifier()\
        .setFeaturesCol('scaledFeatures')\
        .setLabelCol('target')\
        .setMaxDepth(params['maxDepth'])\
        .setNumTrees(params['numTrees'])\

    pipeline = Pipeline(stages = [assembler,scaler,rf])

    rf_model = pipeline.fit(train_data)

    evaluator = BinaryClassificationEvaluator()\
            .setLabelCol('target')

    auc = evaluator.evaluate(rf_model.transform(test_data))

    # with mlflow.start_run():
    #     mlflow.log_params(params)
    #     mlflow.log_metric('auc', auc)

    return {'loss': -auc, 'status': STATUS_OK}


def main():

    logger.info("Creating Spark Session ...")

    spark = SparkSession\
        .builder\
        .appName('Spark ML Research')\
        .config('spark.sql.repl.eagerEval.enabled', True) \
        .getOrCreate()

    logger.info(spark)

    # bucket_name = 'cold-s3-bucket'
    row_path = f"s3a://{bucket_name}/output_data/clean_data.parquet"

    row_sdf = spark.read.parquet(row_path)

    #row_sdf.printSchema()

    agg_cust_path = f"s3a://{bucket_name}/output_data/agg_customer_data.parquet"
    agg_cust_sdf = spark.read.parquet(agg_cust_path)
    #agg_cust_sdf.printSchema()

    agg_term_path = f"s3a://{bucket_name}/output_data/agg_term_data.parquet"
    agg_term_sdf = spark.read.parquet(agg_term_path)
    #agg_term_sdf.printSchema()

    logger.info("data upload ...")

    list_for_fillna = [
    'term_active_days_7d',
     'term_uniq_customer_7d',
     'term_amount_50perc',
     'term_total_cnt_trans_7d',
     'term_amount_max',
     'term_amount_min',
     'term_bad_cnt_trans_7d',
     'term_avg_amount_in_day_7d',
     'term_cnt_in_day_7d',
     'term_days_with_bad_trans_7d',
     'cust_active_days_7d',
     'cust_uniq_terminal_7d',
     'cust_amount_50perc',
     'cust_amount_max',
     'cust_amount_min',
     'cust_total_cnt_trans_7d',
     'cust_bad_cnt_trans_7d',
     'cust_avg_amount_in_day_7d',
     'cust_cnt_in_day_7d',
     'cust_days_with_bad_trans_7d',
     'rel_cust_50perc',
    #  'sh_bad_trans_per_cust',
    #  'sh_bad_trans_per_term',
    #  'sh_bad_days_per_cust',
    #  'sh_bad_days_per_term',
    #  'rel_cust_amount_to_max',
    #  'rel_term_amount_to_max'

    ]

    list_dates= row_sdf.select('date_key').distinct().collect()
    ld = [str(x[0]) for x in list_dates]
    start=min(ld)
    end=max(ld)
    time_keys = [
        time_key.strftime("%Y-%m-%d") for time_key
        in pd.date_range(start, end, freq='1D')
    ]



    train_dates = time_keys[20:23]
    test_dates = time_keys[24]

    logger.info(f"traind perion {train_dates} test period {test_dates}")

    train_sdf = datamart(train_dates,row_sdf,agg_cust_sdf,agg_term_sdf,list_for_fillna,sample_val = 0.5)
    test_sdf = datamart(test_dates,row_sdf,agg_cust_sdf,agg_term_sdf,list_for_fillna,sample_val = 1)

    numericColumnsFinal =['term_amount_min',
         'term_amount_50perc',
         'term_amount_max',
         'tx_amount',
         'term_avg_amount_in_day_7d',
         'sh_bad_trans_per_cust',
         'cust_cnt_in_day_7d',
        # 'tx_fraud',
         'rel_cust_50perc',
         'sh_bad_days_per_term',
         'rel_cust_amount_to_max']

    featureColumns = numericColumnsFinal



    # mlflow.set_experiment('classification')

    trials = Trials()

    #mlflow.set_experiment('classification')

    best = fmin(
        fn=partial(
            objective,
            train_data=train_sdf,
            test_data=test_sdf
        ),
        space=search_space,
        algo=tpe.suggest,
        max_evals=2,
        trials=trials
    )


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--mlflow", required=True, help="Mlflow uri")
    args = parser.parse_args()
    bucket_name = args.bucket
    mlflow_ip = args.mlflow

    # os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://storage.yandexcloud.net'
    # os.environ['MLFLOW_TRACKING_URI']='http://{mlflow_ip}:8000'

    main()
