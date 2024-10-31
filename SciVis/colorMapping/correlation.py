import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

def load_dataset(folder):
    dataset = {}
    for i in os.listdir(folder):
        if i.endswith(".nc"):
            dataset[i.replace(".nc", "")] = xr.open_dataset(f"{folder}/{i}")
    return dataset

def calculate_daily_means(dataset):
    # Dictionary to store mean values for each variable for each date
    data_dict = {"date": []}

    # Iterate over each dataset (assumed to be for each date)
    for date, ds in dataset.items():
        # Add date
        data_dict["date"].append(date)

        # Calculate mean for each variable and store in data_dict
        for var in ds.data_vars:
            if var not in data_dict:
                data_dict[var] = []
            data_dict[var].append(ds[var].mean().item())  # Calculate mean and convert to scalar

    # Convert to a DataFrame
    df = pd.DataFrame(data_dict)
    return df

def plot_correlation_matrix(df):
    # Convert date column to datetime and ordinal (for numerical correlation)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].map(pd.Timestamp.toordinal)

    # Calculate the correlation matrix
    corr_matrix = df.corr()

    # Plot the correlation matrix
    plt.figure(figsize=(15,15))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", square=True, cbar_kws={"shrink": .5})
    plt.title("Correlation Matrix of Variables")
    plt.tight_layout()
    plt.savefig("correlation_matrix.png")
    

if __name__ == "__main__":
    dataset = load_dataset("../sampled_data")

    # Calculate daily mean values for each variable and date
    df = calculate_daily_means(dataset)

    # Plot the correlation matrix
    plot_correlation_matrix(df)
