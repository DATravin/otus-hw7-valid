# import findspark

# findspark.init()

import os
import sys
from loguru import logger
from functools import partial
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
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
from scipy import stats
import numpy as np

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


# # Функция для создания нового эксперимента или поднятия существующего
# def get_experiment_id(model_name):
#     experiment = mlflow.get_experiment_by_name(model_name)
#     if experiment:
#         return experiment.experiment_id
#     else:
#         return mlflow.create_experiment(model_name)


# Функция для регистрации новой модели в mlflow в stage="Staging"
def transit_model(model_name, run_id):
    client = MlflowClient()
    model_uri = "runs:/{}/{}".format(run_id, model_name)
    mv = mlflow.register_model(model_uri, model_name)
    # Если не нужно сразу переводить модель в Staging, то строку ниже закомментировать.
    # В этом случае новая модель или новая версия модели регистрируется в Stage=None
    client.transition_model_version_stage(name=model_name, version=mv.version, stage="Staging")


def get_model(model_name: str, version: str):

    # model_uri: str = f"models:/{model_name}/{model_stage}"
    # model = mlflow.spark.load_model(model_uri)

    model_uri=f'models:/{model_name}/{version}'
    model = mlflow.spark.load_model(model_uri)

    return model


# Функция для смены STAGE по указанной версии модели
def mlflow_change_stage(model_name, version, stage):
    client = MlflowClient()
    mv = client.transition_model_version_stage(model_name, version, stage)

# Определяем пространство поиска для hyperopt
search_space = {
    'numTrees': hp.randint('numTrees', 50, 150),
    'maxDepth': hp.randint('maxDepth', 3,7)
}


def main():


    mlflow.set_experiment('classification')

    model_name = 'classification'

    client = MlflowClient()
    model_versions = client.search_model_versions(filter_string=f"name = '{model_name}'")

    if len(model_versions)==1:
        logger.info("only one version of model. And module")
        sys.exit()


    spark = SparkSession\
        .builder\
        .appName('Spark ML Research')\
        .getOrCreate()

    print('hello')

    #logger.info(spark)

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
    ]

    list_dates= row_sdf.select('date_key').distinct().collect()
    ld = [str(x[0]) for x in list_dates]
    start=min(ld)
    end=max(ld)
    time_keys = [
        time_key.strftime("%Y-%m-%d") for time_key
        in pd.date_range(start, end, freq='1D')
    ]



#     train_dates = time_keys[20:23]
    verif_dates = time_keys[25]

    logger.info(f"test period {verif_dates}")

#     train_sdf = datamart(train_dates,row_sdf,agg_cust_sdf,agg_term_sdf,list_for_fillna,sample_val = 0.5)
    test_sdf = datamart(verif_dates,row_sdf,agg_cust_sdf,agg_term_sdf,list_for_fillna,sample_val = 0.1)


    # bucket_name = 'cold-s3-bucket'
    output_table_path = f"s3a://{temp_bucket_name}/temp_verif.parquet"

    mode ="append"
    fmt= "parquet"

    (test_sdf
     .repartition(1)
     .write
     .format(fmt)
     .mode(mode)
     .save(output_table_path))


    logger.info(f"verif data has been prepared")


    model_metadata = client.get_latest_versions(model_name, stages=["Staging"])
    staging_ver = model_metadata[0].version

    model_metadata = client.get_latest_versions(model_name, stages=["Production"])
    production_ver = model_metadata[0].version


    prod_model = get_model(model_name,production_ver)

    stage_model = get_model(model_name,staging_ver)


    # ver_acrh=0

    # client = MlflowClient()
    # model_versions = client.search_model_versions(filter_string=f"name = '{model_name}'")


    # for ver in model_versions:
    #     if ver.current_stage =='Production':
    #         ver_prod = ver.version
    #     elif ver.current_stage =='Staging':
    #         ver_stage = ver.version
    #     elif ver.current_stage =='Archived':
    #         if int(ver.version)>int(ver_acrh):
    #             ver_acrh = int(ver.version)


#     client = MlflowClient()
#     model_versions = client.search_model_versions(filter_string=f"name = '{model_name}'")
#     model_versions

    evaluator = BinaryClassificationEvaluator()\
            .setLabelCol('target')

    verif_sdf = spark.read.parquet(output_table_path)

    vec1=[]
    vec2=[]

    for i in range(0,50):


        test_date_new = verif_sdf.sample(0.33)


        auc1 = evaluator.evaluate(prod_model.transform(test_date_new))
        auc2 = evaluator.evaluate(stage_model.transform(test_date_new))

        vec1.append(auc1)
        vec2.append(auc2)

        # with mlflow.start_run() as run:

        #     mlflow.log_metric('auc_cur', auc1)
        #     mlflow.log_metric('auc_new', auc2)


    logger.info(f"experement has been done")

    t, p_value  = stats.ttest_ind(vec1, vec2)

    alpha = 0.05


    if p_value < alpha:

        if np.mean(vec2)>np.mean(vec1):
            logger.info(f"new model is better")

            client.transition_model_version_stage(name=model_name, version=staging_ver, stage="Production")
            client.transition_model_version_stage(name=model_name, version=production_ver, stage="None")


        elif np.mean(vec2)<np.mean(vec1):
            logger.info(f"old model is better")
            client.transition_model_version_stage(name=model_name, version=staging_ver, stage="None")

    else:
        logger.info(f"there is no difference between models")
        client.transition_model_version_stage(name=model_name, version=staging_ver, stage="None")




if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--mlflow", required=True, help="Mlflow uri")
    parser.add_argument("--aws_acc", required=True, help="AWS accses key")
    parser.add_argument("--aws_sec", required=True, help="AWS secret key")
    parser.add_argument("--bucket_art", required=True, help="S3 bucket name for artifacts")
    args = parser.parse_args()
    bucket_name = args.bucket
    mlflow_ip = args.mlflow
    aws_acc = args.aws_acc
    aws_sec = args.aws_sec
    temp_bucket_name = args.bucket_art

    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://storage.yandexcloud.net'
    os.environ['MLFLOW_TRACKING_URI'] = f'http://{mlflow_ip}:8000'
    os.environ["AWS_ACCESS_KEY_ID"] = f'{aws_acc}'
    os.environ["AWS_SECRET_ACCESS_KEY"] = f'{aws_sec}'
    os.environ["S3_ENDPOINT_URL"] = 'https://storage.yandexcloud.net'
    os.environ["S3_BUCKET_NAME"] = temp_bucket_name

    main()
