import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def process_severity_data(file_paths, year_column='Start_Year',
                          duration_column='Duration', ys_column='YS',
                          severity_column='Severity'):
    severity_mapping = {
        'mild': 1,
        'moderate': 2,
        'severe': 3,
        'extreme': 4,
        'na': np.nan,
        'nan': np.nan,
        '': np.nan
    }
    
    all_data = []
    for file_path in file_paths:
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            print(f"Successfully read file: {file_path}, Rows: {len(df)}")
            
            required_cols = [year_column, duration_column, ys_column, severity_column]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            df = df.copy()
            df[year_column] = pd.to_numeric(df[year_column], errors='coerce')
            df.rename(columns={year_column: 'Year'}, inplace=True)
            
            df[severity_column] = df[severity_column].astype('object').fillna('nan').str.lower()
            df['Severity_Numeric'] = df[severity_column].map(severity_mapping)
            
            missing_severity = df['Severity_Numeric'].isnull().sum()
            if missing_severity > 0:
                invalid_values = df[df['Severity_Numeric'].isnull()][severity_column].value_counts().head(10)
                print(f"Warning: {missing_severity} records in {file_path} have unconvertible Severity")
                print(f"Top 10 unconvertible Severity values:\n{invalid_values}")
            
            valid_df = df.dropna(subset=['Year', 'Severity_Numeric', duration_column, ys_column]).copy()
            valid_df['Year'] = valid_df['Year'].astype(int)
            all_data.append(valid_df)
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            continue
            
    if not all_data:
        raise ValueError("No valid data to process. Please check file paths and column names.")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    yearly_stats = combined_df.groupby('Year').agg(
        Duration_Sum=(duration_column, 'sum'),
        Duration_Mean=(duration_column, 'mean'),
        YS_Sum=(ys_column, 'sum'),
        YS_Mean=(ys_column, 'mean'),
        Avg_Severity=('Severity_Numeric', 'mean'),
        Record_Count=('Severity_Numeric', 'count')
    ).round(2).reset_index().sort_values('Year').reset_index(drop=True)
    
    return yearly_stats


def save_results(results, output_path='yearly_severity_stats.xlsx'):
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        results.to_excel(writer, sheet_name='Yearly_Stats', index=False)
    print(f"Results saved to: {output_path}")


def calculate_and_plot_area_ratio():
    file1 = pd.read_excel(r'D:\pythonProject\sensitivity_test\10\10_1980-1999_data.xlsx')
    file2 = pd.read_excel(r'D:\pythonProject\sensitivity_test\10\10_1999-2020_data.xlsx')
    data = pd.concat([file1, file2], ignore_index=True)
    
    print("Data loaded and merged successfully. First few rows:")
    print(data.head())
    
    total_grids = 96793
    
    data['Grid'] = data['Lat'].astype(str) + ',' + data['Lon'].astype(str)
    
    annual_drought_grids = data.groupby('Start_Year')['Grid'].nunique().reset_index()
    annual_drought_grids.columns = ['Year', 'Drought_Grid_Count']
    annual_drought_grids['Area_Index'] = annual_drought_grids['Drought_Grid_Count'] / total_grids * 100
    
    print("\nAnnual Drought Area Index:")
    print(annual_drought_grids)
    
    pentad_drought_grids = data.groupby(['Start_Year', 'Condition'])['Grid'].nunique().reset_index()
    pentad_drought_grids.columns = ['Year', 'hou', 'Drought_Grid_Count']
    pentad_drought_grids['Area_Index'] = pentad_drought_grids['Drought_Grid_Count'] / total_grids * 100
    
    print("\nPentad Drought Area Index:")
    print(pentad_drought_grids)
    
    pentad1 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('1-pentad', na=False)]
    pentad2 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('2-pentad', na=False)]
    pentad3 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('3-pentad', na=False)]
    pentad4 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('4-pentad', na=False)]
    
    print("\nPentad 1 data:")
    print(pentad1)
    print("\nPentad 2 data:")
    print(pentad2)
    print("\nPentad 3 data:")
    print(pentad3)
    print("\nPentad 4 data:")
    print(pentad4)
    
    plt.figure(figsize=(12, 8))
    plt.bar(annual_drought_grids['Year'], annual_drought_grids['Area_Index'], color='grey', label='Total events')
    plt.xlabel('Year')
    plt.ylabel('Area Index (%)')
    plt.title('Annual Drought Area Index (1980-2020)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    plt.figure(figsize=(12, 8))
    plt.plot(pentad1['Year'], pentad1['Area_Index'], marker='o', label='1-pentad events', color='purple')
    plt.plot(pentad2['Year'], pentad2['Area_Index'], marker='o', label='2-pentad events', color='black')
    plt.plot(pentad3['Year'], pentad3['Area_Index'], marker='o', label='3-pentad events', color='blue')
    plt.plot(pentad4['Year'], pentad4['Area_Index'], marker='o', label='4-pentad events', color='red')
    plt.xlabel('Year')
    plt.ylabel('Area Index (%)')
    plt.title('Pentad Drought Area Index (1980-2020)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    excel_files = [
        r'D:\pythonProject\sensitivity_test\10\10_1980-1999_data.xlsx',
        r'D:\pythonProject\sensitivity_test\10\10_1999-2020_data.xlsx'
    ]
    
    YEAR_COLUMN = 'Start_Year'
    DURATION_COLUMN = 'Duration'
    YS_COLUMN = 'YS'
    SEVERITY_COLUMN = 'Severity'
    
    OUTPUT_FILE = r'D:\pythonProject\sensitivity_test\10\yearly_severity_stats.xlsx'
    
    try:
        stats_results = process_severity_data(
            file_paths=excel_files,
            year_column=YEAR_COLUMN,
            duration_column=DURATION_COLUMN,
            ys_column=YS_COLUMN,
            severity_column=SEVERITY_COLUMN
        )
        print("\n=== Yearly Severity Statistics ===")
        print(stats_results)
        save_results(stats_results, OUTPUT_FILE)
    except Exception as e:
        print(f"Error during severity processing: {str(e)}")
    
    try:
        calculate_and_plot_area_ratio()
    except Exception as e:
        print(f"Error during area ratio calculation: {str(e)}")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file1 = pd.read_excel(r'D:\pythonProject\sensitivity_test\10\10_1980-1999_data.xlsx')
file2 = pd.read_excel(r'D:\pythonProject\sensitivity_test\10\10_1999-2020_data.xlsx')

data = pd.concat([file1, file2], ignore_index=True)

print("Data loaded and merged successfully. First few rows:")
print(data.head())

total_grids = 96793

data['Grid'] = data['Lat'].astype(str) + ',' + data['Lon'].astype(str)

annual_drought_grids = data.groupby('Start_Year')['Grid'].nunique().reset_index()
annual_drought_grids.columns = ['Year', 'Drought_Grid_Count']
annual_drought_grids['Area_Index'] = annual_drought_grids['Drought_Grid_Count'] / total_grids * 100

print("\nAnnual Drought Area Index:")
print(annual_drought_grids)

pentad_drought_grids = data.groupby(['Start_Year', 'Condition'])['Grid'].nunique().reset_index()
pentad_drought_grids.columns = ['Year', 'hou', 'Drought_Grid_Count']
pentad_drought_grids['Area_Index'] = pentad_drought_grids['Drought_Grid_Count'] / total_grids * 100

print("\nPentad Drought Area Index:")
print(pentad_drought_grids)

pentad1 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('1-pentad', na=False)]
pentad2 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('2-pentad', na=False)]
pentad3 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('3-pentad', na=False)]
pentad4 = pentad_drought_grids[pentad_drought_grids['hou'].str.contains('4-pentad', na=False)]

print("\nPentad 1 data:")
print(pentad1)
print("\nPentad 2 data:")
print(pentad2)
print("\nPentad 3 data:")
print(pentad3)
print("\nPentad 4 data:")
print(pentad4)

plt.figure(figsize=(12, 8))
plt.bar(annual_drought_grids['Year'], annual_drought_grids['Area_Index'], color='grey', label='Total events')
plt.xlabel('Year')
plt.ylabel('Area Index (%)')
plt.title('Annual Drought Area Index (1980-2020)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 8))
plt.plot(pentad1['Year'], pentad1['Area_Index'], marker='o', label='1-pentad events', color='purple')
plt.plot(pentad2['Year'], pentad2['Area_Index'], marker='o', label='2-pentad events', color='black')
plt.plot(pentad3['Year'], pentad3['Area_Index'], marker='o', label='3-pentad events', color='blue')
plt.plot(pentad4['Year'], pentad4['Area_Index'], marker='o', label='4-pentad events', color='red')
plt.xlabel('Year')
plt.ylabel('Area Index (%)')
plt.title('Pentad Drought Area Index (1980-2020)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

