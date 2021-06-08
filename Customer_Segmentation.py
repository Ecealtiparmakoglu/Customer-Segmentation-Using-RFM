import pandas as pd
import datetime as dt
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

#A quick view to dataset
df = pd.read_excel("dataset.xlsx", sheet_name="Year 2010-2011")
df.head()
df.describe().T
df.isnull().sum()

#Missing values are removed from the dataset.
df.dropna(inplace=True)
df.isnull().sum()

#Unique number of products
df['StockCode'].nunique()

#How many of each product?
df.groupby('StockCode').value_counts()

#5 most ordered products
df.groupby('StockCode').agg({'Quantity': 'count'}).sort_values(by="Quantity", ascending=False).head()

#Canceled transactions are removed from the dataset
df = df[~df['Invoice'].str.contains('C', na=False)]

#Calculated total price
df["TotalPrice"] = df["Price"] * df["Quantity"]
df.head()

#Recency:time since last purchase
#Frequency:frequency of purchase
#Monetary: amount of purchase

#Calculation of Recency, Frequency and Monetary metrics specific to the customer
df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate:(today_date - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "TotalPrice": lambda TotalPrice: TotalPrice.sum()})
rfm.head()

#Converting Recency, Frequency and Monetary metrics to 1-5 scores with the qcut function
rfm['Recency_Score'] = pd.qcut(rfm['Recency'], 5 , labels=[5,4,3,2,1])

rfm['Frequency_Score'] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1,2,3,4,5])

rfm['Monetary_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])

#3 different variable values are saved as a single variable
rfm['RFM_SCORE'] = (rfm['Recency_Score'].astype(str) +
                    rfm['Frequency_Score'].astype(str))
                    #rfm['Monetary_Score'].astype(str))

#converting scores into segments with the help of a dictionary
#NOTE: segments are made only for recency and frequency values, monetary is not included!
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['SEGMENT'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

#Analyzes can be made for related variables by grouping according to segments.
rfm[["SEGMENT", "Recency", "Frequency", "Monetary"]].groupby("SEGMENT").agg(["mean", "count"])