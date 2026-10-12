import pandas as pd

# Sample data
data = {
    'Region': ['UK', 'UK', 'France', 'France', 'Germany', 'Germany'],
    'Revenue': [120, 150, 200, 220, 300, 330],
    'Quantity': [10, 12, 15, 18, 20, 25]
}

df = pd.DataFrame(data) # convert into table

print('\n Below is the table \n')
print(df.head(6))
print('\n')

# Aggregation
summary = df.groupby('Region').agg({ 'Revenue': ['sum', 'mean'], 'Quantity': 'sum', })

#sort by revenue
revenue_sum = summary.sort_values(('Revenue','sum'),ascending=False)

print(summary)
print('\n Highest total revenue ')
print(revenue_sum)


#show region sold most
region_most = revenue_sum.head(1)
print(f"\n\n\nRegion with the most items sold:",region_most)

'''
Formula
Mean = sum of all values /  number of values

TASK : which region has Highest total revenue
hint :  = df.groupby("Item")["Quantity"].sum().sort_values(ascending=False).head(5)

TASK: which region sold the most items(Quantity sum)
'''