import xarray as xr
import os
# Load the data
def slice_data(ds,days=("2018-07-01","2018-09-30")):
    return ds.sel(day=slice(*days))

def create_new_dataset(files):
    for file in files:
        ds = xr.open_dataset("./dataset/"+file)
        ds = slice_data(ds)
        ds.to_netcdf("./modified_dataset/"+file)
if __name__=="__main__":
    files = os.listdir("dataset")    
    os.makedirs("modified_dataset",exist_ok=True)
    create_new_dataset(files)
