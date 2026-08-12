import numpy as np
import rasterio
import pandas as pd
import matplotlib.pyplot as plt

def read_tiff(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)
    return data


severity_data = read_tiff(r'E:\data_organization\3.1_original_raster\raster\severity_1980-2020.tif')
intensity_data = read_tiff(r'E:\data_organization\3.1_original_raster\raster\drought_intensity_1980_2020.tif')

severity_intervals = [0, 50, 100, 150, np.inf]
intensity_intervals = [1, 2, 3, 4, np.inf]

severity_categories = np.digitize(severity_data, severity_intervals)
intensity_categories = np.digitize(intensity_data, intensity_intervals)

interaction_matrix = np.zeros((len(severity_intervals)-1, len(intensity_intervals)-1))

for i in range(1, len(severity_intervals)):
    for j in range(1, len(intensity_intervals)):
        mask = (severity_categories == i) & (intensity_categories == j)
        interaction_matrix[i-1, j-1] = np.sum(mask)

row_sums = interaction_matrix.sum(axis=1, keepdims=True)
interaction_percentage = interaction_matrix / row_sums * 100

columns = [f"{intensity_intervals[i]}-{intensity_intervals[i+1]}%" for i in range(len(intensity_intervals)-1)]
index = [f"{severity_intervals[i]}-{severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)]

df_freq = pd.DataFrame(interaction_matrix, columns=columns, index=index)
df_percent = pd.DataFrame(interaction_percentage, columns=columns, index=index)

with pd.ExcelWriter('severity_intensity_interaction_1980-2020.xlsx') as writer:
    df_freq.to_excel(writer, sheet_name='Counts')
    df_percent.to_excel(writer, sheet_name='Row Percentages')

print("Interaction data saved as 'severity_intensity_interaction_1980-2020.xlsx'")

plt.figure(figsize=(10, 6))
plt.imshow(interaction_percentage, cmap='YlOrRd', aspect='auto')
plt.colorbar(label='Percentage (%)')
plt.xticks(np.arange(len(columns)), columns)
plt.yticks(np.arange(len(index)), index)
plt.xlabel('Intensity (%)')
plt.ylabel('Severity')
plt.title('Severity vs. Intensity Interaction (%)')
plt.tight_layout()
plt.show()


severity_data = read_tiff(r'E:\data_organization\3.1_original_raster\raster\drought_intensity_1980_2020.tif')
duration_data = read_tiff(r'E:\data_organization\3.1_original_raster\raster\drought_duration_mean_1980-2023.tif')

duration_intervals = [(3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11)]
severity_intervals = [1, 2, 3, 4, np.inf]
severity_categories = np.digitize(severity_data, severity_intervals)

duration_categories = np.zeros_like(duration_data)
for i, (start, end) in enumerate(duration_intervals):
    duration_categories = np.where((duration_data >= start) & (duration_data < end), i + 1, duration_categories)

interaction_data = np.zeros((len(duration_intervals), len(severity_intervals) - 1))

for i, (start, end) in enumerate(duration_intervals):
    for j, severity in enumerate(range(1, len(severity_intervals))):
        mask = (duration_categories == i + 1) & (severity_categories == severity)
        interaction_data[i, j] = np.sum(mask)

interaction_percentages = interaction_data / np.sum(interaction_data, axis=1, keepdims=True) * 100
total_interaction = np.sum(interaction_data)
total_percentages = interaction_data / total_interaction * 100

interaction_df = pd.DataFrame(interaction_data, columns=[f"Severity {severity_intervals[i]} - {severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)],
                              index=[f"Duration {start}-{end}" for start, end in duration_intervals])

interaction_percentage_df = pd.DataFrame(interaction_percentages, columns=[f"Severity {severity_intervals[i]} - {severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)],
                                           index=[f"Duration {start}-{end}" for start, end in duration_intervals])

total_percentage_df = pd.DataFrame(total_percentages, columns=[f"Severity {severity_intervals[i]} - {severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)],
                                    index=[f"Duration {start}-{end}" for start, end in duration_intervals])

with pd.ExcelWriter('duration_intensity_interaction_1980-2020_modified.xlsx') as writer:
    interaction_df.to_excel(writer, sheet_name='Interaction Data')
    interaction_percentage_df.to_excel(writer, sheet_name='Interaction Percentages')
    total_percentage_df.to_excel(writer, sheet_name='Total Percentages')

print("Excel file saved as 'duration_intensity_interaction_1980-2020_modified.xlsx'")

plt.figure(figsize=(15, 10))

plt.subplot(1, 3, 1)
plt.imshow(interaction_data, cmap='YlGnBu', aspect='auto')
plt.colorbar(label='Count')
plt.title('Interaction Data Heatmap')
plt.xlabel('Severity')
plt.ylabel('Duration')
plt.xticks(np.arange(len(severity_intervals)-1), [f"{severity_intervals[i]}-{severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)])
plt.yticks(np.arange(len(duration_intervals)), [f"{start}-{end}" for start, end in duration_intervals])

plt.subplot(1, 3, 2)
plt.imshow(interaction_percentages, cmap='YlGnBu', aspect='auto')
plt.colorbar(label='Percentage (%)')
plt.title('Interaction Percentages Heatmap')
plt.xlabel('Severity')
plt.ylabel('Duration')
plt.xticks(np.arange(len(severity_intervals)-1), [f"{severity_intervals[i]}-{severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)])
plt.yticks(np.arange(len(duration_intervals)), [f"{start}-{end}" for start, end in duration_intervals])

plt.subplot(1, 3, 3)
plt.imshow(total_percentages, cmap='YlGnBu', aspect='auto')
plt.colorbar(label='Total Percentage (%)')
plt.title('Total Percentages Heatmap')
plt.xlabel('Severity')
plt.ylabel('Duration')
plt.xticks(np.arange(len(severity_intervals)-1), [f"{severity_intervals[i]}-{severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)])
plt.yticks(np.arange(len(duration_intervals)), [f"{start}-{end}" for start, end in duration_intervals])

plt.tight_layout()
plt.show()


severity_data = read_tiff(r'E:\data_organization\3.1_original_raster\raster\severity_1980-1999.tif')
duration_data = read_tiff(r'E:\data_organization\3.1_original_raster\raster\drought_duration_0.1deg_1980-1999.tif')

duration_intervals = [(3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11)]
severity_intervals = [0, 50, 100, 150, np.inf]
severity_categories = np.digitize(severity_data, severity_intervals)

duration_categories = np.zeros_like(duration_data)
for i, (start, end) in enumerate(duration_intervals):
    duration_categories = np.where((duration_data >= start) & (duration_data < end), i + 1, duration_categories)

interaction_data = np.zeros((len(duration_intervals), len(severity_intervals) - 1))

for i, (start, end) in enumerate(duration_intervals):
    for j, severity in enumerate(range(1, len(severity_intervals))):
        mask = (duration_categories == i + 1) & (severity_categories == severity)
        interaction_data[i, j] = np.sum(mask)

interaction_percentages = interaction_data / np.sum(interaction_data, axis=1, keepdims=True) * 100

interaction_df = pd.DataFrame(interaction_data, columns=[f"Severity {severity_intervals[i]} - {severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)],
                              index=[f"Duration {start}-{end}" for start, end in duration_intervals])

interaction_percentage_df = pd.DataFrame(interaction_percentages, columns=[f"Severity {severity_intervals[i]} - {severity_intervals[i+1]}" for i in range(len(severity_intervals)-1)],
                                           index=[f"Duration {start}-{end}" for start, end in duration_intervals])

with pd.ExcelWriter('duration_severity_interaction_1980-1999_modified.xlsx') as writer:
    interaction_df.to_excel(writer, sheet_name='Interaction Data')
    interaction_percentage_df.to_excel(writer, sheet_name='Interaction Percentages')

print("Excel file saved as 'duration_severity_interaction_1980-1999_modified.xlsx'")
