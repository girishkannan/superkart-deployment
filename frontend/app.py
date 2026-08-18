# Importing the required libraries
import streamlit as st       # To build the interactive web UI
import pandas as pd          # To handle the uploaded batch data
import requests              # To call the Flask backend API

# Base URL of the backend. "superkart-backend" is the name of the backend container
# on the shared Docker network, so the frontend container can reach it by that name.
BACKEND_URL = "http://superkart-backend:7860"

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")

st.title("🛒 SuperKart Sales Forecasting")
st.write(
    "Predict the total sales revenue of a product in a store. "
    "Use **Online Prediction** for a single product or **Batch Prediction** for a CSV file."
)

tab1, tab2 = st.tabs(["Online Prediction", "Batch Prediction"])

# --------------------------- Online prediction ---------------------------
with tab1:
    st.subheader("Enter the product and store details")

    col1, col2 = st.columns(2)

    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0,
                                         value=12.66, step=0.01)
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0,
                                      value=117.08, step=0.01)
        product_allocated_area = st.number_input("Product Allocated Area", min_value=0.0,
                                                 max_value=1.0, value=0.027, step=0.001,
                                                 format="%.3f")
        product_sugar_content = st.selectbox("Product Sugar Content",
                                             ["Low Sugar", "Regular", "No Sugar"])
        product_id_char = st.selectbox("Product Category Code",
                                       ["FD", "DR", "NC"],
                                       help="FD - Food, DR - Drinks, NC - Non-Consumable")

    with col2:
        product_type_category = st.selectbox("Product Type Category",
                                             ["Perishables", "Non Perishables"])
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("Store Location City Type",
                                                ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type",
                                  ["Departmental Store", "Supermarket Type1",
                                   "Supermarket Type2", "Food Mart"])
        store_age_years = st.number_input("Store Age (years)", min_value=0, max_value=100,
                                          value=16, step=1)

    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar_content,
        "Product_Allocated_Area": product_allocated_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_location_city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": store_age_years,
        "Product_Type_Category": product_type_category,
    }

    if st.button("Predict Sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted sales"]
                st.success(f"Predicted sales revenue: **{prediction:,.2f}**")
            else:
                st.error(f"Request failed with status code {response.status_code}")
        except Exception as e:
            st.error(f"Could not reach the backend API: {e}")

# --------------------------- Batch prediction ----------------------------
with tab2:
    st.subheader("Upload a CSV file for batch prediction")
    st.caption(
        "The file must contain the columns: Product_Weight, Product_Sugar_Content, "
        "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, "
        "Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category"
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write("Preview of the uploaded data:")
        st.dataframe(batch_df.head())

        if st.button("Run Batch Prediction", type="primary"):
            try:
                uploaded_file.seek(0)
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": uploaded_file.getvalue()},
                    timeout=120,
                )
                if response.status_code == 200:
                    preds = pd.Series(response.json()).astype(float)
                    preds.index = preds.index.astype(int)
                    batch_df["Predicted_Sales"] = preds.sort_index().values
                    st.success("Batch prediction completed")
                    st.dataframe(batch_df)
                    st.download_button(
                        "Download predictions as CSV",
                        data=batch_df.to_csv(index=False).encode("utf-8"),
                        file_name="superkart_predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"Request failed with status code {response.status_code}")
            except Exception as e:
                st.error(f"Could not reach the backend API: {e}")
