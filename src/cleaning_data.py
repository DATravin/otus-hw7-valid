"""
модуль для очистки данных
Для запуска в качестве параметра подается
название файла на hdfs

Результат:
очищенный файл в формате parquet

Пример запуска c мастер ноды:

python3 cleaning_data.py -fn '2022-11-04.txt'

"""
import findspark

findspark.init()

from loguru import logger
#import argparse
from argparse import ArgumentParser
import sys
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.types import IntegerType,LongType,DoubleType,StringType

data_path = "/user/ubuntu/data/"

# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--file_name",
#         "-fn",
#         help="name of file on hdfs",
#         required=True,
#         type=str,
#         dest="file_name",
#     )

#     args = parser.parse_args()
#     return args

# генерация названия файлика-лога
def get_spark():

    spark = (
            SparkSession
            .builder
            .appName("OTUS")
            .getOrCreate()
            )
    return spark

def transform_data(input_path,output_path):

    logger.info("Spark session has been estableshed")

    findspark.init()
    logger.info("Spark init - done")

    spark = get_spark()
    logger.info("Spark session has been estableshed")

    logger.info("check_existing_new_data")

    try:
        df_exists = spark.read.parquet(output_path)
        partitions = (df_exists
                    .select('date_key')
                    .distinct()
                    .withColumn('date_key', F.col('date_key').cast(StringType()))
                    .distinct()
                   ).collect()

        ex_partitions = [str(row[0]) for row in partitions]

    except Exception:

        logger.info("There is no data")
        ex_partitions = []


    logger.info(f"Existing partitions: {ex_partitions}")


    logger.info(f"read data from : {input_path}")

    sdf = spark.read.text(input_path)

    split_col = F.split(sdf['value'], ',')

    sdf_split = (sdf
                .withColumn('tranaction_id', split_col.getItem(0))
                .withColumn('tx_datetime', split_col.getItem(1))
                .withColumn('customer_id', split_col.getItem(2))
                .withColumn('terminal_id', split_col.getItem(3))
                .withColumn('tx_amount', split_col.getItem(4))
                .withColumn('tx_time_seconds', split_col.getItem(5))
                .withColumn('tx_time_days', split_col.getItem(6))
                .withColumn('tx_fraud', split_col.getItem(7))
                .withColumn('tx_fraud_scenario', split_col.getItem(8))
                .drop(*['value'])
                .filter(~F.lower(F.col('tranaction_id')).like('%tranaction_id%'))
                .withColumn('date_key', F.to_date(F.col('tx_datetime')))
                .withColumn('date_key', F.col('date_key').cast(StringType()))
                .filter(~F.col('date_key').isin(ex_partitions))
               )

    if sdf_split.count()==0:
        logger.info("There is no new partitions")
        sys.exit()
    else:
        logger.info("There is new partitions. Start cleaning")






    sdf_agg = (
                sdf_split
                .select(*['tx_amount'])
                .dropna()
                .agg(
                    F.round(F.expr("percentile(tx_amount, array(0.01))")[0], 4).alias("tx_amount_1perc"),
                    F.round(F.expr("percentile(tx_amount, array(0.99))")[0], 4).alias("tx_amount_99perc")
                    )
               )

    col_list = [
                'tranaction_id',
                'tx_datetime',
                'customer_id',
                'terminal_id',
                'tx_amount',
                'tx_time_seconds',
                'tx_time_days',
                'tx_fraud',
                'tx_fraud_scenario',
                'date_key'
                ]

    sdf_clean = (
                sdf_split
                .join(sdf_agg, how='left')
                .filter(F.col('tx_amount')>0)
                .filter(F.col('tx_amount')>=F.col('tx_amount_1perc'))
                .filter(F.col('tx_amount')<=F.col('tx_amount_99perc'))
                .dropna()
                .filter(~F.col('terminal_id').rlike('[a-zA-Z]')) # только альфа-нумерик
                .filter(~F.col('customer_id').rlike('[a-zA-Z]')) # только альфа-нумерик
                .filter(~F.col('tranaction_id').rlike('[a-zA-Z]')) # только альфа-нумерик
                .filter(~F.col('tx_fraud').rlike('[a-zA-Z]')) # только альфа-нумерик
                .filter(~F.col('tx_fraud_scenario').rlike('[a-zA-Z]')) # только альфа-нумерик
                .filter(F.col('tx_time_seconds')>0) # только альфа-нумерик
                .filter(F.col('tx_time_days')>0) # только альфа-нумерик
                .select(*col_list)
                .distinct()
                .withColumn('tranaction_id', F.col('tranaction_id').cast(StringType()))
                .withColumn('tx_datetime', F.col('tx_datetime').cast(StringType()))
                .withColumn('customer_id', F.col('customer_id').cast(StringType()))
                .withColumn('terminal_id', F.col('terminal_id').cast(StringType()))
                .withColumn('tx_amount', F.col('tx_amount').cast(DoubleType()))
                .withColumn('tx_time_seconds', F.col('tx_time_seconds').cast(LongType()))
                .withColumn('tx_time_days', F.col('tx_time_days').cast(LongType()))
                .withColumn('tx_fraud', F.col('tx_fraud').cast(IntegerType()))
                .withColumn('tx_fraud_scenario', F.col('tx_fraud_scenario').cast(IntegerType()))

                )

    mode ="append"
    fmt= "parquet"
    partition_cols= ("date_key",),

    num_out_partitions=1

    if num_out_partitions:
        sdf_clean = sdf_clean.repartition(num_out_partitions)

    (
    sdf_clean
     .write
     .format(fmt)
     .mode(mode)
     .partitionBy(*partition_cols)
     .save(output_path)
    )

    logger.info(f"data has been saved to : {output_path} succesfully")
    logger.info("job is done")


def main():
    """Main function to execute the PySpark job"""
    parser = ArgumentParser()
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    args = parser.parse_args()
    bucket_name = args.bucket

    if not bucket_name:
        raise ValueError("Environment variable S3_BUCKET_NAME is not set")

    input_path = f"s3a://{bucket_name}/input_data/*.txt"
    output_path = f"s3a://{bucket_name}/output_data/clean_data.parquet"

    transform_data(input_path, output_path)



if __name__ == '__main__':
    main()
