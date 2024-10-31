import xarray as xr
import matplotlib.pyplot as plt
import os

def load_dataset(folder): # Load the dataset
    dataset = {}
    for i in os.listdir(folder):
        if i.endswith(".nc"):
            ds=xr.open_dataset(f"{folder}/{i}")
            add_calculated_field(ds)
            ds=normalize_data(ds)
            dataset[i.replace(".nc", "")] = ds
    return dataset

def add_calculated_field(ds):
    ds["Correlation Hazard Score"]=(ds["air_temperature"]*0.1-0.73*ds["precipitation_amount"]-0.38*ds["relative_humidity"]+0.34*ds["potential_evapotranspiration"]+0.22*ds["wind_speed"]+0.36*ds["energy_release_component-g"])/(0.1+0.73+0.38+0.34+0.22+0.36)
    
def normalize_data(ds): 
    return (ds-ds.min())/(ds.max()-ds.min())

def plot_variable_over_time(dataset, variable_name, title, cmap, ax, date_index, frame,add_color_bar=False):
    # Concatenate all time slices from datasets for the variable
    data_stack = xr.concat([dataset[key][variable_name] for key in dataset], dim='time')
    
    # Plot for the specific frame
    img = ax.imshow(data_stack.isel(time=frame), cmap=cmap)
    ax.set_title(f"{title} - {date_index[frame]}")
    if add_color_bar:
        plt.colorbar(img, ax=ax, fraction=0.046, pad=0.04, shrink=0.7)

def save_images(output_dir,dataset, date_index, num_images=10,cmap="viridis"):
    
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Plot and save each frame as a separate image
    for frame in range(min(num_images, len(date_index))):
        fig, axs = plt.subplots(2,1, figsize=(10, 10))

        # Plot each variable in its respective subplot
        plot_variable_over_time(dataset, "burning_index_g", "Burning Index", cmap, axs[0], date_index, frame,True)
        plot_variable_over_time(dataset, "Correlation Hazard Score", "Fire Hazard Score", cmap, axs[1], date_index, frame,True)
        

        # Save the figure
        file_path = os.path.join(output_dir, f"frame_{frame}.png")
        plt.savefig(file_path)
        plt.close(fig)  

if __name__ == "__main__":
    dataset = load_dataset("../sampled_data")

    date_index = list(dataset.keys())
    output_dirs=["bad_corr_fig_inferno"]
    for output_dir in output_dirs:
        save_images(output_dir,dataset, date_index, num_images=10,cmap=output_dir.split("_")[-1])
    
