# import findspark

# findspark.init()

# from loguru import logger
# from argparse import ArgumentParser
import sys
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.types import IntegerType,LongType,DoubleType,StringType


def main():

    spark = SparkSession\
        .builder\
        .appName('Spark ML Research')\
        .getOrCreate()

    print('hello')

if __name__ == "__main__":

    main()
