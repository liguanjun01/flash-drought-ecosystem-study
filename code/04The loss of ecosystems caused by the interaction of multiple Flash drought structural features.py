==============================
%Classification of Severity of FlashDrought

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = r'C:\Users\Yinyufei\Desktop\data_statistics\transit1.xlsx'
df = pd.read_excel(file_path)

def classify_severity(severity):
    if severity < 50:
        return '<50'
    elif 50 <= severity < 100:
        return '50-100'
    elif 100 <= severity < 150:
        return '100-150'
    else:
        return '>150'

df['Severity_Category'] = df['Severity'].apply(classify_severity)

df['<50'] = df['GPP_Loss'].where(df['Severity_Category'] == '<50')
df['50-100'] = df['GPP_Loss'].where(df['Severity_Category'] == '50-100')
df['100-150'] = df['GPP_Loss'].where(df['Severity_Category'] == '100-150')
df['>150'] = df['GPP_Loss'].where(df['Severity_Category'] == '>150')

result = df[['Severity', 'GPP_Loss', '<50', '50-100', '100-150', '>150']]

result.to_excel('SIF_recovery_test.xlsx', index=False)

print("Results saved as 'SIF_recovery_test.xlsx'")

=====================

%The loss of ecosystems caused by the interaction of multiple sudden drought structural features

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import seaborn as sns

file_path = r"E:\pythonProject\gpp_summary_5.25.xlsx"
data = pd.read_excel(file_path)

condition_mapping = {'mild': 1, 'moderate': 2, 'severe': 3, 'extreme': 4}
data['Intensity'] = data['Intensity'].map(condition_mapping)

grouped_data = data.groupby(['Intensity', 'Duration_y'])['GPPLOSSS'].mean().reset_index()

pivot_table = grouped_data.pivot(index='Intensity', columns='Duration_y', values='GPPLOSSS')

pivot_table.to_excel("Average_gpp_Loss_by_Intensity_and_Duration5.29.xlsx")

plt.figure(figsize=(12, 8))
sns.heatmap(
    pivot_table,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    cbar_kws={'label': 'Average GPP_Loss'}
)

plt.title("Average GPP_Loss by Condition and Duration", fontsize=16)
plt.xlabel("Duration (hou)", fontsize=12)
plt.ylabel("Condition (1=one, 2=two, 3=three, 4=four)", fontsize=12)

plt.tight_layout()
plt.show()

def categorize_severity(Severity_y):
    if Severity_y < 50:
        return 'Low (<50)'
    elif 50 <= Severity_y < 100:
        return 'Medium (50-100)'
    elif 100 <= Severity_y < 150:
        return 'High (100-150)'
    else:
        return 'Very High (>150)'

data['Severity_Category'] = data['Severity_y'].apply(categorize_severity)

grouped_condition_severity = data.groupby(['Intensity', 'Severity_Category'])['GPPLOSSS'].mean().reset_index()

pivot_condition_severity = grouped_condition_severity.pivot(index='Intensity', columns='Severity_Category', values='GPPLOSSS')

pivot_condition_severity.to_excel("Average_gpp_Loss_by_Intensity_and_Severity5.29.xlsx")

plt.figure(figsize=(12, 8))
sns.heatmap(
    pivot_condition_severity,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    cbar_kws={'label': 'Average GPP_Loss'}
)
plt.title("Average GPP_Loss by Condition and Severity Category", fontsize=16)
plt.xlabel("Severity Category", fontsize=12)
plt.ylabel("Condition", fontsize=12)
plt.tight_layout()
plt.show()

grouped_severity_duration = data.groupby(['Severity_Category', 'Duration_y'])['GPPLOSSS'].mean().reset_index()

pivot_severity_duration = grouped_severity_duration.pivot(index='Severity_Category', columns='Duration_y', values='GPPLOSSS')

pivot_severity_duration.to_excel("Average_GPP_Loss_by_Severity_and_Duration5.29.xlsx")

plt.figure(figsize=(12, 8))
sns.heatmap(
    pivot_severity_duration,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    cbar_kws={'label': 'Average GPP_Loss'}
)
plt.title("Average GPP_Loss by Severity Category and Duration", fontsize=16)
plt.xlabel("Duration (hou)", fontsize=12)
plt.ylabel("Severity Category", fontsize=12)
plt.tight_layout()
plt.show()