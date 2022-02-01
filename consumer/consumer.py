import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql import SparkSession

def main():
    # write your logic here
    topic = 'prices'
    spark = (
            SparkSession.builder.master("local")
            .appName("Kafka Consumer")
            .getOrCreate()
        )
    spark.sparkContext.setLogLevel("WARN")

    # Setting schema
    schema = T.StructType().add("ts", T.TimestampType()).add("symbol", T.StringType()).add("price", T.DoubleType())
    
    df = spark.read.format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", topic) \
            .load()
    
    # print("#"*80)
    # print("Data from Kafka:")
    # df.show(5)
    # print("#"*80)

    data_df = df.select(F.from_json(F.col("value").cast("string"), schema).alias("parsed_value")).select("parsed_value.*")
    
    print("#"*80)
    print("Printing actual values from the producer:\n")
    data_df.printSchema()
    data_df.show(20)
    print("#"*80)
    print("\n")
    print("#"*80)
    # Print the count of rows in the data
    print("Count of rows:", data_df.count())
    
    print("#"*80)
    print("\n")

    # Aggregate the data by calculating the minimum, maximum, average and standard deviation
    agg_df = data_df.groupby(['symbol']).agg(
        F.min('price').alias('min'), 
        F.max('price').alias('max'), 
        F.mean('price').alias('mean'), 
        F.stddev('price').alias('stddev')
        )
    print("#"*80)
    print("Aggregated data:\n")
    agg_df.show()
    print("#"*80)
    print("\n")

    # Join the statistics calculated above to the actual row-wise data 
    # Compare every price to mean +/- 2 standard deviations and mark the outliers found in the above step
    joined_df = data_df.join(agg_df.select('symbol', 'mean', 'stddev'), on='symbol', how='left')
    joined_df = joined_df.withColumn('outlier_flag', F.when(
        (F.col("price") >= (F.col('mean') + (F.lit(2)*F.col('stddev')))) |
        (F.col("price") < (F.col('mean') - (F.lit(2)*F.col('stddev')))), 1
    ).otherwise(0))

    print("#"*80)
    print("Flagged Outliers:\n")
    joined_df.show()
    print("#"*80)

if __name__ == "__main__":
    main()
