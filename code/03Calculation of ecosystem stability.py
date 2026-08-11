import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

def validate_drought_event(event_period):
    if len(event_period) == 0:
        return False
    mean_anomaly = np.mean(event_period)
    return mean_anomaly < 0

def calculate_drought_metrics(gppsa_data, row_idx, col_idx, event_period, first_negative_idx, min_gpp_idx, start_time_idx, end_time_idx, print_details=False):
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
        return None, None, None, None, None, None
    recovery_time = recovery_idx - abs_min_gpp_idx
    negative_values = extended_period[first_negative_idx:recovery_idx - start_time_idx + 1]
    min_in_neg_idx = min_gpp_idx - first_negative_idx
    time_to_min_gpp = min_in_neg_idx + 1
    loss_until_min = 0.0
    for i in range(1, min_in_neg_idx + 1):
        loss_until_min += abs(negative_values[i] - negative_values[i - 1])
    if print_details:
        print("\n=== GPP Loss Calculation Details ===")
        print("Time series values:")
        for i, value in enumerate(negative_values):
            print(f"Time point {i}: {value:.4f}")
        print(f"\nTime steps from first negative to min: {time_to_min_gpp}")
        print(f"Cumulative loss before min: {loss_until_min:.4f}")
        print("\nDifferences between adjacent points:")
        total_loss = 0
        for i in range(1, len(negative_values)):
            diff = abs(negative_values[i] - negative_values[i - 1])
            total_loss += diff
            print(f"Time point {i - 1} to {i}: |{negative_values[i]:.4f} - {negative_values[i - 1]:.4f}| = {diff:.4f}")
        print(f"\nTotal GPP loss: {total_loss:.4f}")
    gpp_loss = sum(abs(negative_values[i] - negative_values[i - 1]) for i in range(1, len(negative_values)))
    max_negative = min(negative_values)
    return response_time, recovery_time, gpp_loss, max_negative, time_to_min_gpp, loss_until_min

def plot_drought_event(event_id, gppsa_values, time_indices, event_info, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(15, 8))
    time_points = np.arange(len(gppsa_values))
    plt.plot(time_points, gppsa_values, 'b-', label='GPP Anomaly', linewidth=2)
    plt.axhline(y=0, color='k', linestyle='--', label='Zero line', alpha=0.5)
    plt.axvline(x=time_indices['first_negative'], color='g', linestyle='--', label=f"First negative (Day {time_indices['first_negative'] * 5})", alpha=0.5)
    plt.axvline(x=time_indices['min_gpp'], color='y', linestyle='--', label=f"Minimum point (Day {time_indices['min_gpp'] * 5})", alpha=0.5)
    plt.axvline(x=time_indices['recovery'], color='m', linestyle='--', label=f"Recovery point (Day {time_indices['recovery'] * 5})", alpha=0.5)
    plt.axvline(x=event_info['original_end'], color='r', linestyle=':', label='Original event end', alpha=0.5)
    negative_period = time_points[time_indices['first_negative']:time_indices['recovery'] + 1]
    negative_values = gppsa_values[time_indices['first_negative']:time_indices['recovery'] + 1]
    plt.fill_between(negative_period, negative_values, 0, where=(negative_values < 0), color='red', alpha=0.3, label='GPP Loss Area')
    for i in range(len(negative_period) - 1):
        if negative_values[i] < 0 or negative_values[i + 1] < 0:
            plt.annotate('', xy=(negative_period[i + 1], negative_values[i + 1]), xytext=(negative_period[i], negative_values[i]), arrowprops=dict(arrowstyle='<->', color='gray', alpha=0.5))
    plt.title(f"Drought Event {event_id}\n" f"Location: Lat={event_info['lat']:.2f}, Lon={event_info['lon']:.2f}\n" f"Period: {event_info['start_year']}-{event_info['start_hou']} to " f"{event_info['end_year']}-{event_info['end_hou']}")
    plt.xlabel('Time steps (5-day periods)')
    plt.ylabel('GPP Anomaly')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'event_{event_id}.png'), dpi=300, bbox_inches='tight')
    plt.close()

def main():
    output_root = r'D:\FlashDrought_5.18'
    fig_folder = r'D:\FlashDrought_5.18\GPP_Event_Images'
    os.makedirs(output_root, exist_ok=True)
    os.makedirs(fig_folder, exist_ok=True)
    events = pd.read_excel(r'C:\Users\31994\Desktop\gpp.xlsx')
    gppsa_data = np.load(r'D:\FlashDrought_5.18\gpp_standardized.npy')
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
            response_time, recovery_time, gpp_loss, max_negative, time_to_min_gpp, loss_until_min = calculate_drought_metrics(gppsa_data, row_idx, col_idx, event_period, first_negative_idx, min_gpp_idx, start_time_idx, end_time_idx, print_details)
            if print_details and recovery_time is not None:
                printed_count += 1
                print(f"\nEvent ID: {idx}")
                print(f"Location: Lat={event['Lat']}, Lon={event['Lon']}")
                print(f"Time: {event['Start_Year']}-{event['Start_Hou']} to {event['End_Year']}-{event['End_Hou']}")
                print(f"Response Time: {response_time}")
                print(f"Time to Min GPP: {time_to_min_gpp}")
                print(f"Loss Until Min: {loss_until_min:.4f}")
                print(f"Recovery Time: {recovery_time}")
                print(f"Max Negative: {max_negative:.4f}")
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
                'Time_To_Min_GPP': time_to_min_gpp,
                'Loss_Until_Min': loss_until_min,
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
                    time_indices={'first_negative': first_negative_idx, 'min_gpp': min_gpp_idx, 'recovery': recovery_time + min_gpp_idx},
                    event_info={'lat': event['Lat'], 'lon': event['Lon'], 'start_year': event['Start_Year'], 'start_hou': event['Start_Hou'], 'end_year': event['End_Year'], 'end_hou': event['End_Hou'], 'original_end': end_time_idx - start_time_idx},
                    output_dir=fig_folder
                )
        except Exception as e:
            print(f"Error processing event {idx}: {e}")
            continue
    excel_out_path = os.path.join(output_root, 'GPP_Loss.xlsx')
    results_df = pd.DataFrame(results)
    results_df.to_excel(excel_out_path, index=False)
    print("\n=== Statistics ===")
    print(f"Total events: {len(results)}")
    print(f"Events with extended recovery: {results_df['Extended_Recovery'].sum()}")
    print(f"Percentage of extended recovery: {(results_df['Extended_Recovery'].sum() / len(results)) * 100:.2f}%")
    print("\nResponse Time Stats (pentads):")
    print(results_df['Response_Time'].describe())
    print("\nTime To Min GPP Stats (pentads):")
    print(results_df['Time_To_Min_GPP'].describe())
    print("\nLoss Until Min Stats:")
    print(results_df['Loss_Until_Min'].describe())
    print("\nRecovery Time Stats (pentads):")
    print(results_df['Recovery_Time'].describe())
    print("\nTotal GPP Loss Stats:")
    print(results_df['GPP_Loss'].describe())
    print("\nMax Negative Anomaly Stats:")
    print(results_df['Max_Negative'].describe())
    print(f"\n✅ Results saved to: {output_root}")

if __name__ == "__main__":
    main()