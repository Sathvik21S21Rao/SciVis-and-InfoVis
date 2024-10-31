import xarray as xr
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.colors import ListedColormap

def load_dataset(folder):  # Load the dataset
    dataset = {}
    for i in os.listdir(folder):
        if i.endswith(".nc"):
            ds = xr.open_dataset(f"{folder}/{i}")
            add_calculated_field(ds)
            ds = normalize_data(ds)
            dataset[i.replace(".nc", "")] = ds
    return dataset

def normalize_data(ds):
    return (ds - ds.min()) / (ds.max() - ds.min())

def add_calculated_field(ds):
    ds["fire_hazard_score"] = (ds["potential_evapotranspiration"] * 0.34 +
                               ds["wind_speed"] * 0.22 +
                               ds["air_temperature"] * 0.1 +
                               ds["relative_humidity"] * -0.38) / (0.34 + 0.22 + 0.1 + 0.38)

def plot_variable_over_time(dataset, variable_name, title, cmap, ax, date_index, frame, log_scale=False, discrete=False, num_levels=10, add_color_bar=False):
    data_stack = xr.concat([dataset[key][variable_name] for key in dataset], dim='time')
    data = data_stack.isel(time=frame)

    if log_scale:
        data = np.log1p(data)

    if discrete:
        cmap = ListedColormap(plt.get_cmap(cmap)(np.linspace(0, 1, num_levels)))
    else:
        cmap = plt.get_cmap(cmap)

    # Plot the data
    img = ax.imshow(data, cmap=cmap)
    ax.set_title(f"{title} - {date_index[frame]}")
    
    if add_color_bar:
        plt.colorbar(img, ax=ax, fraction=0.046, pad=0.04, shrink=0.7)

def save_images(output_dir, dataset, date_index, num_images=10, cmap="viridis", log_scale=False, discrete=False, num_levels=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Plot and save each frame as a separate image
    for frame in range(min(num_images, len(date_index))):
        fig, axs = plt.subplots(2, 1, figsize=(10, 10))

        plot_variable_over_time(dataset, "burning_index_g", "Burning Index", cmap, axs[0], date_index, frame,
                                log_scale=log_scale, discrete=discrete, num_levels=num_levels, add_color_bar=True)
        plot_variable_over_time(dataset, "fire_hazard_score", "Fire Hazard Score", cmap, axs[1], date_index, frame,
                                log_scale=log_scale, discrete=discrete, num_levels=num_levels, add_color_bar=True)

        # Save the figure
        file_path = os.path.join(output_dir, f"frame_{frame}.png")
        plt.savefig(file_path)
        plt.close(fig)

if __name__ == "__main__":
    dataset = load_dataset("../sampled_data")
    date_index = list(dataset.keys())

    output = [
        {"output_dir": "animation_continuous_inferno", "cmap": "inferno", "log_scale": False, "discrete": False},
        {"output_dir": "animation_log_continuous_inferno", "cmap": "inferno", "log_scale": True, "discrete": False},
        {"output_dir": "animation_discrete_YlOrRd", "cmap": "YlOrRd", "log_scale": False, "discrete": True, "num_levels": 5},
        {"output_dir": "animation_log_discrete_Y1OrRed", "cmap": "YlOrRd", "log_scale": True, "discrete": True, "num_levels": 8}
    ]

    # Generate images for each setting
    for plot in output:
        save_images(plot["output_dir"], dataset, date_index, num_images=10, cmap=plot["cmap"],
                    log_scale=plot.get("log_scale", False), discrete=plot.get("discrete", False),
                    num_levels=plot.get("num_levels", 10))
