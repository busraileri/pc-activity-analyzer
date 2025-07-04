import pandas as pd
import matplotlib.pyplot as plt

# read CSV 
df = pd.read_csv('data/usage_log.csv', header=0)

df["duration"] = df["duration"].astype(int)
total_duration = df['duration'].sum()

print(f"Total usage time: {total_duration // 60} minutes {total_duration % 60} seconds")

# total duration as application
app_usage = df.groupby('app_name')['duration'].sum().sort_values(ascending=False)


# top 5 most used apps
app_usage_min = app_usage / 60
top5_apps = app_usage_min.head(5)

print("\nTop 5 most used applications:")
print(top5_apps)


plt.figure(figsize=(10,6))
top5_apps.plot(kind='bar', color='skyblue')
plt.title('Top 5 Most Used Applications')
plt.xlabel('Application')
plt.ylabel('Total Time (minutes)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
