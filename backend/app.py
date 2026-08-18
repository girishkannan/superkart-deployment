# Importing the required libraries
from flask import Flask, request, jsonify   # Flask web framework
import pandas as pd                          # For handling the input data
import joblib                                # To load the serialized model

# Creating the Flask app
superkart_api = Flask("SuperKart Sales Predictor")

# Loading the serialized model pipeline (preprocessing + regressor)
model = joblib.load("superkart_model.joblib")

# The exact features the model pipeline expects
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health check endpoint."""
    return "Welcome to the SuperKart Sales Prediction API"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online (single record) inference."""
    payload = request.get_json()

    # Converting the JSON payload into a single row dataframe
    input_df = pd.DataFrame([payload])[FEATURES]

    # Predicting the total sales for the product-store combination
    prediction = model.predict(input_df)[0]

    return jsonify({"Predicted sales": round(float(prediction), 2)})


@superkart_api.post("/v1/predictbatch")
def predict_batch():
    """Batch inference - accepts a CSV file and returns a prediction per row."""
    file = request.files["file"]

    # Reading the uploaded CSV into a dataframe
    input_df = pd.read_csv(file)[FEATURES]

    # Predicting the total sales for every row
    predictions = model.predict(input_df)

    # Returning a JSON where each key is the row index and the value is the prediction
    return pd.Series(predictions).astype(float).round(2).to_json(double_precision=2)


if __name__ == "__main__":
    # host 0.0.0.0 makes the API reachable from outside the container
    superkart_api.run(host="0.0.0.0", port=7860, debug=True)
