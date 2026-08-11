====================
%Calculation of ecosystem loss

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os

def validate_drought_event(event_period):
    if len(event_period) == 0:
        return False
    mean_anomaly = np.mean(event_period)
    return mean_anomaly < 0

def calculate_drought_metrics(gppsa_data, row_idx, col_idx, event_period, first_negative_idx, min_gpp_idx,
                              start_time_idx, end_time_idx, print_details=False):
    response_time = first_negative_idx + 1

    extended_end_idx = min(end_time_idx + 40, len(gppsa_data))
    extended_period = gppsa_data[start_time_idx:extended_end_idx, row_idx, col_idx]

    recovery_idx = None
    abs_min_gpp_idx = start_time_idx + min_gpp_idx

    for i in range(abs_min_gpp_idx + 1, extended_end_idx):
        if gppsa_data[i, row_idx, col_idx] >= 0:
            recovery_idx = i
            break

    if recovery_idx is None:
        return None, None, None, None

    recovery_time = recovery_idx - abs_min_gpp_idx

    negative_values = extended_period[first_negative_idx:recovery_idx - start_time_idx + 1]

    if print_details:
        print("\n=== GPP Loss Calculation Details ===")
        print("Time series values:")
        for i, value in enumerate(negative_values):
            print(f"Time point {i}: {value:.4f}")

        print("\nDifferences between adjacent points:")
        total_loss = 0
        for i in range(1, len(negative_values)):
            diff = abs(negative_values[i] - negative_values[i - 1])
            total_loss += diff
            print(f"Difference from time point {i - 1} to {i}: |{negative_values[i]:.4f} - {negative_values[i - 1]:.4f}| = {diff:.4f}")
        print(f"\nTotal GPP Loss: {total_loss:.4f}")

    gpp_loss = sum(abs(negative_values[i] - negative_values[i - 1]) for i in range(1, len(negative_values)))
    max_negative = min(negative_values)

    return response_time, recovery_time, gpp_loss, max_negative

def plot_drought_event(event_id, gppsa_values, time_indices, event_info, output_dir='figures/'):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(15, 8))

    time_points = np.arange(len(gppsa_values))
    plt.plot(time_points, gppsa_values, 'b-', label='GPP Anomaly', linewidth=2)

    plt.axhline(y=0, color='k', linestyle='--', label='Zero line', alpha=0.5)

    plt.axvline(x=time_indices['first_negative'], color='g', linestyle='--',
                label=f"First negative (Day {time_indices['first_negative'] * 5})", alpha=0.5)
    plt.axvline(x=time_indices['min_gpp'], color='y', linestyle='--',
                label=f"Minimum point (Day {time_indices['min_gpp'] * 5})", alpha=0.5)
    plt.axvline(x=time_indices['recovery'], color='m', linestyle='--',
                label=f"Recovery point (Day {time_indices['recovery'] * 5})", alpha=0.5)

    plt.axvline(x=event_info['original_end'], color='r', linestyle=':',
                label='Original event end', alpha=0.5)

    negative_period = time_points[time_indices['first_negative']:time_indices['recovery'] + 1]
    negative_values = gppsa_values[time_indices['first_negative']:time_indices['recovery'] + 1]

    plt.fill_between(negative_period, negative_values, 0,
                     where=(negative_values < 0),
                     color='red', alpha=0.3,
                     label='GPP Loss Area')

    for i in range(len(negative_period) - 1):
        if negative_values[i] < 0 or negative_values[i + 1] < 0:
            plt.annotate('',
                         xy=(negative_period[i + 1], negative_values[i + 1]),
                         xytext=(negative_period[i], negative_values[i]),
                         arrowprops=dict(arrowstyle='<->', color='gray', alpha=0.5))

    plt.title(f"Drought Event {event_id}\n"
              f"Location: Lat={event_info['lat']:.2f}, Lon={event_info['lon']:.2f}\n"
              f"Period: {event_info['start_year']}-{event_info['start_hou']} to "
              f"{event_info['end_year']}-{event_info['end_hou']}")
    plt.xlabel('Time steps (5-day periods)')
    plt.ylabel('GPP Anomaly')

    plt.grid(True, alpha=0.3)

    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'event_{event_id}.png'), dpi=300, bbox_inches='tight')
    plt.close()

def main():
    events = pd.read_excel(r'D:\pythonProject\sensitivity_test\50\2001-2020_drought_events_test50514.xlsx')
    gppsa_data = np.load(r'I:\ERA5\YONGGPPSA_standardized8.31.npy')

    results = []
    printed_count = 0

    for idx, event in events.iterrows():
        try:
            row_idx = int(event['Lat'])
            col_idx = int(event['Lon'])
            start_time_idx = (event['Start_Year'] - 2001) * 73 + event['Start_Hou']
            end_time_idx = (event['End_Year'] - 2001) * 73 + (event['End_Hou'])

            event_period = gppsa_data[start_time_idx:end_time_idx + 1, row_idx, col_idx]

            if not validate_drought_event(event_period):
                continue

            first_negative_idx = 0 if event_period[0] < 0 else next((i for i, v in enumerate(event_period) if v < 0), None)
            if first_negative_idx is None:
                continue

            min_gpp_idx = np.argmin(event_period)

            print_details = random.random() < 0.01 and printed_count < 5

            response_time, recovery_time, gpp_loss, max_negative = calculate_drought_metrics(
                gppsa_data, row_idx, col_idx, event_period, first_negative_idx, min_gpp_idx,
                start_time_idx, end_time_idx, print_details)

            if print_details and recovery_time is not None:
                printed_count += 1
                print(f"\nEvent ID: {idx}")
                print(f"Location: Lat={event['Lat']}, Lon={event['Lon']}")
                print(f"Time: {event['Start_Year']}-{event['Start_Hou']} to {event['End_Year']}-{event['End_Hou']}")
                print(f"Response Time: {response_time}")
                print(f"Recovery Time: {recovery_time}")
                print(f"Max Negative Anomaly: {max_negative:.4f}")
                print("=" * 50)

            if recovery_time is None:
                continue

            results.append({
                'Event_ID': idx,
                'Lat': event['Lat'],
                'Lon': event['Lon'],
                'Start_Year': event['Start_Year'],
                'Start_Hou': event['Start_Hou'],
                'End_Year': event['End_Year'],
                'End_Hou': event['End_Hou'],
                'Response_Time': response_time,
                'Recovery_Time': recovery_time,
                'GPP_Loss': gpp_loss,
                'Max_Negative': max_negative,
                'Extended_Recovery': recovery_time > (end_time_idx - start_time_idx - min_gpp_idx)
            })

            if random.random() < 0.01:
                extended_end_idx = min(end_time_idx + 40, len(gppsa_data))
                extended_period = gppsa_data[start_time_idx:extended_end_idx, row_idx, col_idx]

                plot_drought_event(
                    event_id=idx,
                    gppsa_values=extended_period,
                    time_indices={'first_negative': first_negative_idx,
                                  'min_gpp': min_gpp_idx,
                                  'recovery': recovery_time + min_gpp_idx},
                    event_info={'lat': event['Lat'],
                                'lon': event['Lon'],
                                'start_year': event['Start_Year'],
                                'start_hou': event['Start_Hou'],
                                'end_year': event['End_Year'],
                                'end_hou': event['End_Hou'],
                                'original_end': end_time_idx - start_time_idx}
                )

        except Exception as e:
            print(f"Error processing event {idx}: {e}")
            continue

    results_df = pd.DataFrame(results)
    results_df.to_excel(r'D:\pythonProject\sensitivity_test\50\50_threshold_GPP_loss.xlsx', index=False)

    print("\n=== Statistical Information ===")
    print(f"Total events: {len(results)}")
    print(f"Events with extended recovery: {results_df['Extended_Recovery'].sum()}")
    print(f"Percentage of extended recovery: {(results_df['Extended_Recovery'].sum() / len(results)) * 100:.2f}%")
    print("\nResponse Time Statistics (Days):")
    print(results_df['Response_Time'].describe())
    print("\nRecovery Time Statistics (Days):")
    print(results_df['Recovery_Time'].describe())
    print("\nGPP Loss Statistics:")
    print(results_df['GPP_Loss'].describe())
    print("\nMax Negative Anomaly Statistics:")
    print(results_df['Max_Negative'].describe())


if __name__ == "__main__":
    main()

====================================

%Exclude Other land use types from the ecosystem

import pandas as pd
import numpy as np
import rasterio
import os

def read_tif(tif_file):
    if not os.path.exists(tif_file):
        raise FileNotFoundError(f"File {tif_file} does not exist, please check the file path!")
    dataset = rasterio.open(tif_file)
    data = dataset.read(1)
    return data, dataset

def is_valid_pixel(row, col, tif_data):
    row = int(row)
    col = int(col)
    if 0 <= row < tif_data.shape[0] and 0 <= col < tif_data.shape[1]:
        return True
    return False

def process_excel(excel_file, tif_file):
    df = pd.read_excel(excel_file)
    print(f"Excel data shape: {df.shape}")

    tif_data, dataset = read_tif(tif_file)
    print(f"TIFF data shape: {tif_data.shape}")

    rows_to_remove = []

    for idx, row in df.iterrows():
        row_idx = int(row['Lat'])
        col_idx = int(row['Lon'])

        if is_valid_pixel(row_idx, col_idx, tif_data):
            value = tif_data[row_idx, col_idx]
            if value == 4:
                rows_to_remove.append(idx)
        else:
            print(f"Warning: Coordinates ({row_idx}, {col_idx}) are out of TIFF bounds")

    df_cleaned = df.drop(rows_to_remove)
    output_path = r'D:\pythonProject\sensitivity_test\50\50_threshold_GPP_loss_removed.xlsx'
    df_cleaned.to_excel(output_path, index=False)

    print(f"\nSuccess! Removed {len(rows_to_remove)} rows")
    print(f"Saved to: {output_path}")

tif_file = r'I:\zoning\ai_and_vegetation_zoning\lucc5.tif'
excel_file = r'D:\pythonProject\sensitivity_test\50\50_threshold_GPP_loss.xlsx'

try:
    process_excel(excel_file, tif_file)
except Exception as e:
    print(f"Error: {e}")

=================================

%Statistics by dry and wet climate zones and vegetation types

import numpy as np
import rasterio
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import pandas as pd

matplotlib.rcParams['font.family'] = 'SimHei'
matplotlib.rcParams['axes.unicode_minus'] = False

def read_raster(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)
        nodata_value = src.nodata
    return data, nodata_value

drought_freq, drought_nodata = read_raster(r'D:\pythonProject\sensitivity_test\50\50_GPPloss_removed.tif')

region_type, region_nodata = read_raster(r'C:\Users\Lenovo\Desktop\proposal_yinyufei\result\zone_1_16.tif')

region_labels = [
    'Crop_Arid', 'Forest_Arid', 'Grass_Arid', 'Other_Arid',
    'Crop_SemiArid', 'Forest_SemiArid', 'Grass_SemiArid', 'Other_SemiArid',
    'Crop_SemiHumid', 'Forest_SemiHumid', 'Grass_SemiHumid', 'Other_SemiHumid',
    'Crop_Humid', 'Forest_Humid', 'Grass_Humid', 'Other_Humid'
]

region_drought_freq = {label: [] for label in region_labels}

for i in range(drought_freq.shape[0]):
    for j in range(drought_freq.shape[1]):
        if drought_freq[i, j] == drought_nodata or region_type[i, j] == region_nodata:
            continue

        region_id = int(region_type[i, j])
        if 1 <= region_id <= 16:
            region_label = region_labels[region_id - 1]
            region_drought_freq[region_label].append(drought_freq[i, j])

box_data = [region_drought_freq[label] for label in region_labels]

plt.figure(figsize=(12, 8))
sns.boxplot(data=box_data, showfliers=False)
plt.xticks(rotation=90)
plt.xlabel('Region Type')
plt.ylabel('Flash Drought Frequency')
plt.title('Flash Drought Frequency Distribution by Region Type')
plt.tight_layout()
plt.show()

box_data_df = pd.DataFrame(box_data).T
box_data_df.columns = region_labels

box_data_df.to_csv(r'D:\pythonProject\sensitivity_test\50\50_GPPloss_removed.csv', index=False, encoding='utf-8-sig')

==============================

%Grid calculation of ecosystem loss

import pandas as pd
import numpy as np
import rasterio

excel_file = r'D:\pythonProject\sensitivity_test\50\50_threshold_GPP_loss_removed.xlsx'
df = pd.read_excel(excel_file)

raster_path = r'I:\data_organization\original_soil_moisture\masked_SMroot_1980_0.tif'
with rasterio.open(raster_path) as src:
    width = src.width
    height = src.height
    transform = src.transform
    crs = src.crs

    new_raster_data = np.full((height, width), np.nan, dtype=np.float32)
    count_data = np.zeros((height, width), dtype=np.int32)

    for index, row in df.iterrows():
        lat = int(row['Lat'])
        lon = int(row['Lon'])
        gpp_loss = row['GPP_Loss']

        if np.isnan(new_raster_data[lat, lon]):
            new_raster_data[lat, lon] = gpp_loss
        else:
            new_raster_data[lat, lon] += gpp_loss

        count_data[lat, lon] += 1

    mask = count_data > 0
    new_raster_data[mask] /= count_data[mask]

output_raster_path = r'D:\pythonProject\sensitivity_test\50\50_GPPloss_removed.tif'

with rasterio.open(output_raster_path, 'w', driver='GTiff', count=1, dtype='float32',
                   width=width, height=height, crs=crs, transform=transform) as dst:
    dst.write(new_raster_data, 1)

print(f"Raster file saved to: {output_raster_path}")