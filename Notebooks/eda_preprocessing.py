import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import os

# Load data
data_path = "../data/bank_data_C.csv"
data = pd.read_csv(data_path)

# Date conversion
data['TransactionDate'] = pd.to_datetime(data['TransactionDate'], errors='coerce')
data['CustomerDOB'] = pd.to_datetime(data['CustomerDOB'], errors='coerce')

# Create 'Age' column
today = pd.to_datetime("today")
data['Age'] = (today - data['CustomerDOB']).dt.days // 365
data = data[(data['Age'] >= 18) & (data['Age'] <= 100)]

# Add month for aggregation
data['Month'] = data['TransactionDate'].dt.to_period('M').astype(str)

# Plot: Monthly transaction volume
plt.figure(figsize=(12,6))
data.groupby('Month')['TransactionID'].count().plot(kind='bar', color='skyblue')
plt.title("Monthly Transaction Volume")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plot: Top 10 locations
top_locations = data['CustLocation'].value_counts().head(10)
sns.barplot(x=top_locations.index, y=top_locations.values)
plt.title("Top 10 Customer Locations by Transactions")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plot: Transaction Amount distribution
sns.boxplot(data['TransactionAmount (INR)'])
plt.title("Transaction Amount Distribution")
plt.show()

# Save cleaned data
data.to_csv("../output/cleaned_data.csv", index=False)
