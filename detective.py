import matplotlib.pyplot as plt
import pandas as pd

# Load the dataset
data = pd.read_csv("data.csv")

# Display data information
print(data)
print(data.head(3))  # Added (3) to actually fetch the first 3 rows
print(data.shape)  # (rows,columns)
print(data.columns.tolist())  # list of column names

# View specific columns
print(data["score"])  # every score
print(data["city"])  # every city

# Run calculations
print("How many people:", len(data))
print("Average score:", data["score"].mean())
print("Highest score:", data["score"].max())
print("Lowest score:", data["score"].min())

# Find top performer
top = data["score"].idxmax()  # position of the highest score
print("Top scores:", data.loc[top, "name"])

# Filter high scores
high = data[data["score"] > 80]
print(high)
print("How many scored above 80:", len(high))

# Grouping data
print(data.groupby("city")["score"].mean())

# Plotting the graph
plt.bar(data["name"], data["score"])
plt.title("Scores by person")
plt.xlabel("Name")
plt.ylabel("Score")
plt.savefig("chart.png")
plt.show()
data = pd.read_csv("messy.csv")
print(data.isnull().sum())