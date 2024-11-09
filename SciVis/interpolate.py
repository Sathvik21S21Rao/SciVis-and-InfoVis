import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
from PIL import Image

# Directory containing the .nc files
data_dir = './dataset/sampled_data/'

# Output directory for saving interpolated plots
output_dir = './output_interpolated_images/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to find global min and max wind speeds across all files
def find_global_wind_speed_range(files, data_dir):
    global_min = float('inf')
    global_max = float('-inf')
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        data = xr.open_dataset(file_path)
        wind_speed = data['wind_speed'].values
        file_min = np.nanmin(wind_speed)
        file_max = np.nanmax(wind_speed)
        global_min = min(global_min, file_min)
        global_max = max(global_max, file_max)
    return global_min, global_max

# List of all files in the directory
files = sorted([f for f in os.listdir(data_dir) if f.endswith('.nc')])

# Find global min and max wind speeds
global_min_speed, global_max_speed = find_global_wind_speed_range(files, data_dir)

# Function to interpolate between two datasets (linear interpolation)
def interpolate_between_frames(speed1, direction1, speed2, direction2, fraction):
    speed_interp = speed1 + fraction * (speed2 - speed1)
    direction_interp = direction1 + fraction * (direction2 - direction1)
    return speed_interp, direction_interp

# Function to create quiver plots for a given wind dataset
def create_quiver_plot(lat, lon, speed, direction, global_min_speed, global_max_speed, output_image_path_length, output_image_path_color):
    # Convert wind direction and speed into u and v components for both plots
    u_length_based = -speed * np.sin(np.radians(direction))
    v_length_based = -speed * np.cos(np.radians(direction))

    # For color-based quiver plot (constant u and v)
    u_color_based = -np.sin(np.radians(direction))
    v_color_based = -np.cos(np.radians(direction))

    # ---- First plot (Arrow length represents wind speed) ----
    fig, ax1 = plt.subplots(1, 1, figsize=(9, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax1.add_feature(cfeature.LAND, color='lightgray')
    ax1.coastlines()
    ax1.add_feature(cfeature.BORDERS, linestyle=':')
    quiver_length = ax1.quiver(
        lon, lat, u_length_based, v_length_based, 
        scale=200, width=0.002, headlength=4, headaxislength=3, color='black'
    )
    ax1.set_title('Quiver Plot: Length Represents Wind Speed')
    plt.tight_layout()
    plt.savefig(output_image_path_length)
    plt.close()

    # ---- Second plot (Arrow color represents wind speed) ----
    fig, ax2 = plt.subplots(1, 1, figsize=(9, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax2.add_feature(cfeature.LAND, color='lightgray')
    ax2.coastlines()
    ax2.add_feature(cfeature.BORDERS, linestyle=':')
    quiver_color = ax2.quiver(
        lon, lat, u_color_based, v_color_based, speed, 
        scale=50, cmap='viridis', width=0.002, headlength=4, headaxislength=3,
        clim=(global_min_speed, global_max_speed)  # Setting constant color scale
    )
    cbar = plt.colorbar(quiver_color, ax=ax2, orientation='vertical')
    cbar.set_label('Wind Speed (m/s)')
    ax2.set_title('Quiver Plot: Color Represents Wind Speed (Constant Length)')
    plt.tight_layout()
    plt.savefig(output_image_path_color)
    plt.close()

# Function to generate intermediate frames between two datasets
def generate_interpolated_frames(data1, data2, n_interpolations, idx, output_dir, global_min_speed, global_max_speed):
    # Extract latitude, longitude, wind speed, and direction for both datasets
    lat = data1['lat'].values
    lon = data1['lon'].values
    speed1 = data1['wind_speed'].values
    direction1 = data1['wind_from_direction'].values
    speed2 = data2['wind_speed'].values
    direction2 = data2['wind_from_direction'].values

    for step in range(n_interpolations):
        fraction = step / n_interpolations  # Linear interpolation fraction (0 to 1)
        speed_interp, direction_interp = interpolate_between_frames(speed1, direction1, speed2, direction2, fraction)

        output_image_path_length = os.path.join(output_dir, f'interpolated_quiver_length_{idx:03d}_{step:02d}.png')
        output_image_path_color = os.path.join(output_dir, f'interpolated_quiver_color_{idx:03d}_{step:02d}.png')

        # Create quiver plots for interpolated data
        create_quiver_plot(lat, lon, speed_interp, direction_interp, global_min_speed, global_max_speed, output_image_path_length, output_image_path_color)

# Generate quiver plots for each pair of files with interpolation
n_interpolations = 10  # Number of interpolated steps between two frames
for idx in range(len(files) - 1):
    file_path1 = os.path.join(data_dir, files[idx])
    file_path2 = os.path.join(data_dir, files[idx + 1])

    data1 = xr.open_dataset(file_path1)
    data2 = xr.open_dataset(file_path2)

    print(f"Processing interpolation between {files[idx]} and {files[idx+1]} ...")
    generate_interpolated_frames(data1, data2, n_interpolations, idx, output_dir, global_min_speed, global_max_speed)

# Now, stitch all saved images into two GIFs
length_images = [Image.open(os.path.join(output_dir, f'interpolated_quiver_length_{idx:03d}_{step:02d}.png')) for idx in range(len(files) - 1) for step in range(n_interpolations)]
color_images = [Image.open(os.path.join(output_dir, f'interpolated_quiver_color_{idx:03d}_{step:02d}.png')) for idx in range(len(files) - 1) for step in range(n_interpolations)]

# Save as GIF using Pillow with control over duration (duration in milliseconds)
gif_path_length = os.path.join(output_dir, 'interpolated_quiver_length_animation.gif')
gif_path_color = os.path.join(output_dir, 'interpolated_quiver_color_animation.gif')

length_images[0].save(gif_path_length, save_all=True, append_images=length_images[1:], duration=100, loop=0)  # 100ms per frame
color_images[0].save(gif_path_color, save_all=True, append_images=color_images[1:], duration=100, loop=0)  # 100ms per frame

print(f"GIFs saved at {gif_path_length} and {gif_path_color}")
