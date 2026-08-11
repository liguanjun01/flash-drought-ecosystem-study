import pandas as pd
import pingouin as pg

resistance_files = [
    (r'C:\Users\Yin\Desktop\resistance11.xlsx', 'Resistance1'),
    (r'C:\Users\Yin\Desktop\resistance22.xlsx', 'Resistance2')
]

recovery_files = [
    (r'C:\Users\Yin\Desktop\recovery11.xlsx', 'Recovery1'),
    (r'C:\Users\Yin\Desktop\recovery22.xlsx', 'Recovery2')
]

output_path = r'C:\Users\Yinyufei\Desktop\GPP_Zone_Partial_Corr_Four_Models.xlsx'
writer = pd.ExcelWriter(output_path, engine='openpyxl')

def run_partial_corr(file_path, model_label, y_var, x_vars):
    df = pd.read_excel(file_path)
    regions = df['Region_Type'].unique()

    for region in regions:
        sub_df = df[df['Region_Type'] == region][[y_var] + x_vars].dropna()
        if sub_df.shape[0] < 5:
            continue

        results = []
        for i, xi in enumerate(x_vars):
            control_vars = [v for j, v in enumerate(x_vars) if j != i]
            result = pg.partial_corr(data=sub_df, x=xi, y=y_var, covar=control_vars, method='pearson')
            results.append({
                'Variable1': y_var,
                'Variable2': xi,
                'Control_Variables': ', '.join(control_vars),
                'Partial_Corr': round(result['r'].values[0], 4),
                'P_Value': round(result['p-val'].values[0], 4)
            })

        result_df = pd.DataFrame(results)
        result_df = pd.concat([
            pd.DataFrame({'Model': [f'[{region}]{model_label}']}),
            result_df,
            pd.DataFrame({'Model': [None]}),
        ], axis=0)

        sheet_name = f'{model_label}_{region}'[:31]
        result_df.to_excel(writer, sheet_name=sheet_name, index=False)

for file_path, label in resistance_files:
    run_partial_corr(file_path, label, 'Resistance', ['Response_Time', 'GPPLOSSS'])

for file_path, label in recovery_files:
    run_partial_corr(file_path, label, 'Recovery', ['Recovery_Time', 'GPPLOSSS'])

writer.close()
print(f"Partial correlation analysis completed. Results saved to: {output_path}")