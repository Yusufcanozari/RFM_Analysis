import pandas as pd
import datetime as dt
df_ = pd.read_excel(r"C:\Users\Sony\PycharmProjects\pythonProject1\CRM Analytics\online_retail_II.xlsx",sheet_name="Year 2009-2010")
pd.set_option("display.max_columns",None)
pd.set_option("display.float_format",lambda x: "%.3f" % x)
df = df_.copy()
df.head()
# 1. Veri Hazırlama
# 2. Average Order Value (average_order_value = total_price / total_transaction)
# 3. Purchase Frequency (total_transaction / total_number_of_customers)
# 4. Repeat Rate & Churn Rate (birden fazla alışveriş yapan müşteri sayısı / tüm müşteriler)
# 5. Profit Margin (profit_margin =  total_price * 0.10)
# 6. Customer Value (customer_value = average_order_value * purchase_frequency)
# 7. Customer Lifetime Value (CLTV = (customer_value / churn_rate) x profit_margin)
# 8. Segmentlerin Oluşturulması
# 9. BONUS: Tüm İşlemlerin Fonksiyonlaştırılması

# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

df_.info()
df.head()
df.shape
df.isnull().sum()

df["Description"].nunique()
df["Description"].value_counts().head()
df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head()
df["Invoice"].nunique()
df["totalbill"] = df["Price"] * df["Quantity"]
df.groupby("Invoice")["totalbill"].sum()
##################################################################################
#veri temizleme
df.isnull().sum()
df.dropna(inplace=True)
df.describe().T
df = df[~df["Invoice"].str.contains("C", na=False)]# C içermeyenleri getir dedik
##################################################################################
#Rfm Metriklerini hesaplamak
#recency , frequency , monetary

today_date = dt.datetime(2010,12,11)#bu güne göre recencyi hesaplayacağız
Rfm= df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date-date.max()).days,
                                        'Invoice': lambda x: x.nunique(),
                                        'totalbill': lambda x: x.sum()})

Rfm.columns = ["Recency","Frequency","Monetary"]
Rfm.describe().T
Rfm=Rfm[Rfm["Monetary"] > 0]
Rfm.shape


rfm = df.groupby("Customer ID").agg({"InvoiceDate":lambda x:(today_date-x.max()).days,
                                     "Invoice":lambda x:x.nunique(),
                                     "totalbill":lambda x:x.sum()})
rfm.columns = ["Recency","Frequency","Monetary"]
##################################################################################
#Rfm skorlarnın hesaplanması

rfm["recency_score"] = pd.qcut(rfm["Recency"],5,labels=[5,4,3,2,1])#değer skalası burada önemli çünkü reguencyde sıklık ne kadar azsa o kadar yüksek puan alır buu yüzden 5ten başladık normalde kücükten büyüğye gider
rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
rfm["monetary_score"] = pd.qcut(rfm["Monetary"],5,labels=[1,2,3,4,5])

rfm["rfm_score"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
rfm[rfm["rfm_score"] == "55"]#şampiyonlar
rfm[rfm["rfm_score"] == "11"]#önemsizler

##################################################################################
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

rfm["segment"] = rfm["rfm_score"].replace(seg_map,regex=True)
fan = ["segment","Recency","Frequency","Monetary"]
rfm[fan].groupby("segment").agg(["mean","count"])

rfm[rfm["segment"] == "cant_loose"]
rfm[rfm["segment"] == "cant_loose"].index

new_df = pd.DataFrame()
new_df["new_customers"] = rfm[rfm["segment"] == "new_customers"].index
new_df["new_customers"] = new_df["new_customers"].astype(int)
new_df.to_csv("new_customers.csv")
##################################################################################
