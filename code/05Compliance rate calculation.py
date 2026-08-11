=========================
%Data standardization exception

import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from collections import defaultdict

tif_dir = r"E:\GPP_SIF\GPP\processed_data\available_2"
tif_files = [os.path.join(tif_dir, f) for f in os.listdir(tif_dir) if f.endswith('.tif')]

tif_files.sort(key=lambda x: (int(x.split('_')[3]), int(x.split('_')[4].split('.')[0])))

data_list = []
info_list = []

for tif_file in tif_files:
    base_name = os.path.basename(tif_file)
    parts = base_name.split('_')
    year = int(parts[3])
    pentad = int(parts[4].split('.')[0])

    with rasterio.open(tif_file) as src:
        data = src.read(1)
    data_list.append(data)
    info_list.append((year, pentad))

pentad_group = defaultdict(list)
for idx, (year, pentad) in enumerate(info_list):
    pentad_group[pentad].append(data_list[idx])

mean_gpp = {}
std_gpp = {}

for pentad, group in pentad_group.items():
    group_arr = np.array(group)
    mean_gpp[pentad] = np.mean(group_arr, axis=0)
    std_gpp[pentad] = np.std(group_arr, axis=0)

gppsa_list = []

for idx, (year, pentad) in enumerate(info_list):
    arr = data_list[idx]
    with np.errstate(divide='ignore', invalid='ignore'):
        standardized = (arr - mean_gpp[pentad]) / std_gpp[pentad]
    standardized[np.isnan(standardized)] = 0
    gppsa_list.append(standardized)

gppsa_array = np.array(gppsa_list)
print("Shape of the final GPPSA array:", gppsa_array.shape)

plt.imshow(gppsa_array[0], cmap='coolwarm')
plt.colorbar(label='GPPSA')
plt.title('GPPSA for first time period (Year: {}, Pentad: {})'.format(info_list[0][0], info_list[0][1]))
plt.show()

output_file = "GPPSA_standardized8.31.npy"
np.save(output_file, gppsa_array)
print(f"GPPSA has been saved as {output_file}")

==============================
%Compliance rate calculation

import rasterio
import numpy as np
import os
import pandas as pd

events = pd.read_excel(r'D:\pythonProject\sensitivity_test\50\2001-2020_drought_events_test50514.xlsx')

gppsa_data = np.load(r'I:\ERA5\SIFA_standardized.npy', allow_pickle=True)

response_count = np.zeros((gppsa_data.shape[1], gppsa_data.shape[2]))
total_events = np.zeros((gppsa_data.shape[1], gppsa_data.shape[2]))
response_duration = np.zeros((gppsa_data.shape[1], gppsa_data.shape[2]))

tif_dir = r"I:\GPP_SIF\SIF\available_2"
tif_files = sorted([os.path.join(tif_dir, f) for f in os.listdir(tif_dir) if f.endswith('.tif')])

with rasterio.open(tif_files[0]) as src:
    crs = src.crs
    transform = src.transform

for index, row in events.iterrows():
    start_year = row['Start_Year']
    start_hou = row['Start_Hou']
    end_year = row['End_Year']
    end_hou = row['End_Hou']
    lat = row['Lat']
    lon = row['Lon']

    row_idx = int(lat)
    col_idx = int(lon)

    start_time_idx = (start_year - 2001) * 73 + start_hou
    end_time_idx = (end_year - 2001) * 73 + (end_hou - 1)

    gppsa_values = gppsa_data[start_time_idx:end_time_idx + 1, row_idx, col_idx]

    total_events[row_idx, col_idx] += 1

    mean_anomaly = np.mean(gppsa_values)

    if mean_anomaly < 0:
        response_count[row_idx, col_idx] += 1

    negative_start = None
    for i, value in enumerate(gppsa_values):
        if value < 0:
            if negative_start is None:
                negative_start = i
        elif negative_start is not None:
            response_duration[row_idx, col_idx] += i - negative_start
            negative_start = None

    if negative_start is not None:
        response_duration[row_idx, col_idx] += len(gppsa_values) - negative_start

response_frequency = np.zeros_like(response_count, dtype=np.float32)
with np.errstate(divide='ignore', invalid='ignore'):
    response_frequency = np.true_divide(response_count, total_events)
    response_frequency[total_events == 0] = np.nan

with rasterio.open('50_threshold_SIF_compliance_rate_5.14.tif', 'w',
                   driver='GTiff',
                   height=response_frequency.shape[0],
                   width=response_frequency.shape[1],
                   count=1,
                   dtype=rasterio.float32,
                   crs=crs,
                   transform=transform) as dst:
    dst.write(response_frequency, 1)

print("Response frequency calculation completed.")

with rasterio.open('C-SIF_super_test_2.tif', 'w',
                   driver='GTiff',
                   height=response_duration.shape[0],
                   width=response_duration.shape[1],
                   count=1,
                   dtype=rasterio.float32,
                   crs=crs,
                   transform=transform) as dst:
    dst.write(response_duration, 1)

print("Response duration calculation completed.")

for index, row in events.iterrows():
    start_year = row['Start_Year']
    start_hou = row['Start_Hou']
    end_year = row['End_Year']
    end_hou = row['End_Hou']
    lat = int(row['Lat'])
    lon = int(row['Lon'])

    start_time_idx = (start_year - 2001) * 73 + start_hou
    end_time_idx = (end_year - 2001) * 73 + (end_hou - 1)

    gppsa_values = gppsa_data[start_time_idx:end_time_idx + 1, lat, lon]

    mean_anomaly = np.mean(gppsa_values)

    if np.any(gppsa_values < 0):
        print(f"Validation drought event: Start_Year={start_year}, Start_Hou={start_hou}, End_Year={end_year}, End_Hou={end_hou}, Lat={lat}, Lon={lon}")
        print(f"GPPSA data (during event): {gppsa_values}")
        print(f"Mean anomaly during event: {mean_anomaly}")
        print(f"Negative anomaly exists during event: {'Yes' if np.any(gppsa_values < 0) else 'No'}")
        break