import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# Load the dataset
path = './dataset/sampled_data/2018-07-01.nc'
data = xr.open_dataset(path)

# Extracting wind speed and direction
wind_speed = data['wind_speed']
wind_dir = data['wind_from_direction']

# Latitude and longitude from the dataset
lat = wind_speed['lat'].values
lon = wind_speed['lon'].values
speed = wind_speed.values  # Wind speed data
direction = wind_dir.values  # Wind direction data

# Create 2D grids for latitudes and longitudes
lon_grid, lat_grid = np.meshgrid(lon, lat)

# Flatten arrays for easier manipulation (turning them into 1D arrays)
lon_flat = lon_grid.flatten()
lat_flat = lat_grid.flatten()
speed_flat = speed.flatten()
direction_flat = direction.flatten()

# Bin the latitudes and longitudes into 2-degree intervals
lat_bins = np.arange(np.floor(lat_flat.min()), np.ceil(lat_flat.max()) + 2, 2)
lon_bins = np.arange(np.floor(lon_flat.min()), np.ceil(lon_flat.max()) + 2, 2)

# Create pandas DataFrame to handle binning
df = pd.DataFrame({
    'lat': lat_flat,
    'lon': lon_flat,
    'speed': speed_flat,
    'direction': direction_flat
})

# Add binned columns for latitude and longitude (grouping by 2-degree bins)
df['lat_bin'] = pd.cut(df['lat'], bins=lat_bins, labels=lat_bins[:-1] + 1)
df['lon_bin'] = pd.cut(df['lon'], bins=lon_bins, labels=lon_bins[:-1] + 1)

# Group by the binned lat/lon and calculate the mean wind speed and wind direction for each bin
df_grouped = df.groupby(['lat_bin', 'lon_bin']).agg({
    'speed': 'mean',
    'direction': 'mean'
}).reset_index()

# Extract binned data
lat_binned = df_grouped['lat_bin'].astype(float).values
lon_binned = df_grouped['lon_bin'].astype(float).values
speed_binned = df_grouped['speed'].values
direction_binned = df_grouped['direction'].values

# Convert wind direction into u and v components (constant length for quiver)
u_color_based_binned = -np.sin(np.radians(direction_binned))
v_color_based_binned = -np.cos(np.radians(direction_binned))

# Create 2D grids for binned latitudes and longitudes
lon_grid_binned, lat_grid_binned = np.meshgrid(lon_bins[:-1] + 1, lat_bins[:-1] + 1)

# List of colormaps to use
colormaps = ['viridis', 'plasma', 'inferno', 'cividis']

# Create a figure with 4 subplots (2x2 grid) with geographic projection
fig, axes = plt.subplots(2, 2, figsize=(20, 12), subplot_kw={'projection': ccrs.PlateCarree()})

# Adjust land color to a light gray for all subplots and add coastlines and borders
for ax in axes.flatten():
    ax.add_feature(cfeature.LAND, color='lightgray')
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    # Add formatted latitude and longitude tick labels
    ax.set_xticks(np.arange(np.floor(lon.min()), np.ceil(lon.max()) + 5, 5), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(np.floor(lat.min()), np.ceil(lat.max()) + 5, 5), crs=ccrs.PlateCarree())
    
    lon_formatter = LongitudeFormatter(degree_symbol='°')
    lat_formatter = LatitudeFormatter(degree_symbol='°')
    
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

# Loop through the axes and apply different colormaps
for ax, cmap in zip(axes.flatten(), colormaps):
    quiver_color = ax.quiver(
        lon_binned, lat_binned, u_color_based_binned, v_color_based_binned, speed_binned, 
        scale=100, cmap=cmap, width=0.0002, headlength=4, headaxislength=3
    )
    # Add a colorbar for each subplot
    cbar = plt.colorbar(quiver_color, ax=ax, orientation='vertical')
    cbar.set_label('Wind Speed (m/s)')
    ax.set_title(f'Quiver Plot: Colormap = {cmap}')

# Show the combined plot with all colormaps
plt.tight_layout()
plt.show()
