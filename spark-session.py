from pyspark.sql.functions import col, date_format
from flask import Flask, request, jsonify
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import pandas as pd
import traceback
import os

spark = SparkSession.builder \
    .appName("ueh_flask_server") \
    .enableHiveSupport() \
    .getOrCreate()

app = Flask(__name__)
PORT = os.getenv('CDSW_APP_PORT', '8090')

def convert_temporal_columns(df):
    """Convert timestamp/date columns to strings for Pandas compatibility."""
    for field in df.schema.fields:
        dtype = str(field.dataType)
        if "Timestamp" in dtype or "Date" in dtype:
            df = df.withColumn(field.name, F.col(field.name).cast("string"))
    return df

def apply_pagination(df, page, page_size):
    """Apply offset-based pagination to DataFrame."""
    offset = (page - 1) * page_size
    return df.withColumn("_rn", F.row_number().over(Window.orderBy(F.lit(1)))) \
             .filter(F.col("_rn").between(offset + 1, offset + page_size)) \
             .drop("_rn")

@app.route("/query", methods=["GET", "POST"])
def query():
    try:
        # Extract SQL query
        sql = request.args.get("sql") or (request.json or {}).get("sql")
        if not sql:
            return jsonify({"error": "Missing 'sql' parameter"}), 400
        
        # Execute query
        df = spark.sql(sql)
        
        # Convert temporal columns to strings
        df = convert_temporal_columns(df)
        
        # Handle pagination if requested
        page = request.args.get("page", type=int)
        page_size = request.args.get("page_size", type=int)
        
        if page and page_size:
            df = apply_pagination(df, page, page_size)
        
        # Convert to JSON-serializable format
        data = df.toPandas().to_dict(orient="records")
        
        # Build response
        response = {"status": "success", "count": len(data), "data": data}
        if page and page_size:
            response.update({"page": page, "page_size": page_size})
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def health():
    return jsonify({"status": "ok", "message": "UEH Spark API running!"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(PORT))