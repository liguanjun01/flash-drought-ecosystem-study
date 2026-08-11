=========================
%Soil Moisture Percentile Calculation
clear;
clc;
[aadata, R] = geotiffread('I:\DataArrangement\RawSoilMoisture\masked_SMroot_1980_0.tif');
info = geotiffinfo('I:\DataArrangement\RawSoilMoisture\masked_SMroot_1980_0.tif');

[row, col] = size(aadata);
begin_year = 1980;
end_year = 2020;

mst = 0;
med = 72;
save_folder = 'I:\DataArrangement\CP';

for n = 0:72
    PH_data = zeros(end_year - begin_year + 1, row, col, 'single');
    TH_data = zeros(end_year - begin_year + 1, row, col, 'single');
    HH_data = zeros(end_year - begin_year + 1, row, col, 'single');

    for year = begin_year:end_year
        if n == 0
            tem_PH = imread(['I:\DataArrangement\RawSoilMoisture\masked_SMroot_', num2str(year), '_72.tif']);
        else
            tem_PH = imread(['I:\DataArrangement\RawSoilMoisture\masked_SMroot_', num2str(year), '_', num2str(n-1), '.tif']);
        end
        tem_PH(tem_PH > 1) = NaN;
        PH_data(year - begin_year + 1, :, :) = tem_PH;

        tem_TH = imread(['I:\DataArrangement\RawSoilMoisture\masked_SMroot_', num2str(year), '_', num2str(n), '.tif']);
        tem_TH(tem_TH > 1) = NaN;
        TH_data(year - begin_year + 1, :, :) = tem_TH;

        if n == 72
            tem_HH = imread(['I:\DataArrangement\RawSoilMoisture\masked_SMroot_', num2str(year), '_0.tif']);
        else
            tem_HH = imread(['I:\DataArrangement\RawSoilMoisture\masked_SMroot_', num2str(year), '_', num2str(n+1), '.tif']);
        end
        tem_HH(tem_HH > 1) = NaN;
        HH_data(year - begin_year + 1, :, :) = tem_HH;
    end

    for k = 1:row
        for h = 1:col
            datasum_ph = PH_data(:, k, h);
            datasum_th = TH_data(:, k, h);
            datasum_hh = HH_data(:, k, h);
            datasum_all = [datasum_ph; datasum_th; datasum_hh];
            sort_data = sort(datasum_all(~isnan(datasum_all)));

            for i = 1:length(datasum_th)
                if isnan(datasum_th(i))
                    data_hsort(i, k, h) = -9999;
                else
                    sort_numb = find(sort_data == datasum_th(i), 1);
                    percentile = (sort_numb / length(sort_data)) * 100;
                    data_hsort(i, k, h) = percentile;
                end
            end
        end
    end

    save(fullfile(save_folder, ['data_hsort_', num2str(n+1), '.mat']), 'data_hsort');
end

if ~exist('combined_data', 'dir')
    mkdir('combined_data');
end

for i = 1:41
    for n = 1:73
        data = load(['data_hsort_', num2str(n), '.mat']);
        data = data.data_hsort(i, :, :);
        save(['combined_data/data_', num2str(n), '_', num2str(i), '.mat'], 'data');
    end
end

combined_data = zeros(2993, 518, 631);

for year = 1:41
    for hou = 1:73
        filename = sprintf('combined_data/data_%d_%d.mat', hou, year);
        data = load(filename);
        index = (year - 1) * 73 + hou;
        combined_data(index, :, :) = data.data;
    end
end

disp(size(combined_data));

============================================

%Identify Flash drought
drought_count_1 = 0;
drought_events_1 = {};
grid_drought_count_1 = zeros(size(combined_data, 2), size(combined_data, 3));
grid_drought_duration_1 = zeros(size(combined_data, 2), size(combined_data, 3));
grid_drought_severity_1 = zeros(size(combined_data, 2), size(combined_data, 3));

drought_count_2 = 0;
drought_events_2 = {};
grid_drought_count_2 = zeros(size(combined_data, 2), size(combined_data, 3));
grid_drought_duration_2 = zeros(size(combined_data, 2), size(combined_data, 3));
grid_drought_severity_2 = zeros(size(combined_data, 2), size(combined_data, 3));

for hou = 5:size(combined_data, 1)
    current_year = floor((hou - 1) / 73) + 1980;
    
    for lat_index = 1:size(combined_data, 2)
        for lon_index = 1:size(combined_data, 3)
            percentile = combined_data(hou, lat_index, lon_index);

            if percentile <= 20
                meet_condition = false;
                drought_condition = '';
                decline_rate = 0;

                if combined_data(hou-1, lat_index, lon_index) >= 40
                    meet_condition = true;
                    decline_rate = (combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index)) / 1;
                elseif combined_data(hou-2, lat_index, lon_index) >= 40 && ...
                        (combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index) >= 5) && ...
                        (combined_data(hou-2, lat_index, lon_index) - combined_data(hou-1, lat_index, lon_index) >= 5)
                    meet_condition = true;
                    decline_rate = (combined_data(hou-2, lat_index, lon_index) - combined_data(hou, lat_index, lon_index)) / 2;
                elseif combined_data(hou-3, lat_index, lon_index) >= 40 && ...
                        (combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index) >= 5) && ...
                        (combined_data(hou-2, lat_index, lon_index) - combined_data(hou-1, lat_index, lon_index) >= 5) && ...
                        (combined_data(hou-3, lat_index, lon_index) - combined_data(hou-2, lat_index, lon_index) >= 5)
                    meet_condition = true;
                    decline_rate = (combined_data(hou-3, lat_index, lon_index) - combined_data(hou, lat_index, lon_index)) / 3;
                elseif combined_data(hou-4, lat_index, lon_index) >= 40 && ...
                        (combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index) >= 5) && ...
                        (combined_data(hou-2, lat_index, lon_index) - combined_data(hou-1, lat_index, lon_index) >= 5) && ...
                        (combined_data(hou-3, lat_index, lon_index) - combined_data(hou-2, lat_index, lon_index) >= 5) && ...
                        (combined_data(hou-4, lat_index, lon_index) - combined_data(hou-3, lat_index, lon_index) >= 5)
                    meet_condition = true;
                    decline_rate = (combined_data(hou-4, lat_index, lon_index) - combined_data(hou, lat_index, lon_index)) / 4;
                end

                if meet_condition
                    drought_start_hou = hou;
                    drought_duration = 1;

                    for next_hou = hou+1:size(combined_data, 1)
                        next_percentile = combined_data(next_hou, lat_index, lon_index);
                        if next_percentile >= 20
                            drought_end_hou = next_hou;
                            drought_duration = drought_end_hou - drought_start_hou;

                            if drought_duration >= 3 && drought_duration < 12
                                if decline_rate > 20
                                    severity = 'extreme';
                                elseif decline_rate > 15
                                    severity = 'severe';
                                elseif decline_rate > 10
                                    severity = 'moderate';
                                elseif decline_rate > 5
                                    severity = 'mild';
                                else
                                    severity = 'none';
                                end

                                YS = sum(combined_data(drought_start_hou:drought_end_hou, lat_index, lon_index) ...
                                         .* (combined_data(drought_start_hou:drought_end_hou, lat_index, lon_index) <= 20));

                                start_year = floor((drought_start_hou - 1) / 73) + 1980;
                                if start_year <= 1999
                                    drought_count_1 = drought_count_1 + 1;
                                    drought_events_1{drought_count_1} = struct('start_hou', drought_start_hou, ...
                                        'duration', drought_duration, 'end_hou', drought_end_hou, ...
                                        'lat', lat_index, 'lon', lon_index, ...
                                        'condition', drought_condition, 'severity', severity, ...
                                        'intensity', decline_rate, 'YS', YS);
                                else
                                    drought_count_2 = drought_count_2 + 1;
                                    drought_events_2{drought_count_2} = struct('start_hou', drought_start_hou, ...
                                        'duration', drought_duration, 'end_hou', drought_end_hou, ...
                                        'lat', lat_index, 'lon', lon_index, ...
                                        'condition', drought_condition, 'severity', severity, ...
                                        'intensity', decline_rate, 'YS', YS);
                                end
                            end
                            break;
                        end
                    end
                end
            end
        end
    end
end

grid_average_duration_1 = zeros(size(combined_data, 2), size(combined_data, 3));
grid_average_severity_1 = zeros(size(combined_data, 2), size(combined_data, 3));
nonzero_indices_1 = grid_drought_count_1 > 0;
grid_average_duration_1(nonzero_indices_1) = grid_drought_duration_1(nonzero_indices_1) ./ grid_drought_count_1(nonzero_indices_1);
grid_average_severity_1(nonzero_indices_1) = grid_drought_severity_1(nonzero_indices_1) ./ grid_drought_count_1(nonzero_indices_1);

grid_average_duration_2 = zeros(size(combined_data, 2), size(combined_data, 3));
grid_average_severity_2 = zeros(size(combined_data, 2), size(combined_data, 3));
nonzero_indices_2 = grid_drought_count_2 > 0;
grid_average_duration_2(nonzero_indices_2) = grid_drought_duration_2(nonzero_indices_2) ./ grid_drought_count_2(nonzero_indices_2);
grid_average_severity_2(nonzero_indices_2) = grid_drought_severity_2(nonzero_indices_2) ./ grid_drought_count_2(nonzero_indices_2);

if drought_count_1 > 0
    drought_data_1 = cell(drought_count_1, 11);
    drought_data_index = 1;
    
    for i = 1:drought_count_1
        start_year = floor((drought_events_1{i}.start_hou - 1) / 73) + 1980;
        start_hour_in_year = mod(drought_events_1{i}.start_hou - 1, 73) + 1;
        end_year = floor((drought_events_1{i}.end_hou - 1) / 73) + 1980;
        end_hour_in_year = mod(drought_events_1{i}.end_hou - 1, 73) + 1;
        
        if start_hour_in_year >= 19 && start_hour_in_year <= 55 && end_hour_in_year >= 19 && end_hour_in_year <= 55
            drought_data_1{drought_data_index, 1} = start_year;
            drought_data_1{drought_data_index, 2} = start_hour_in_year;
            drought_data_1{drought_data_index, 3} = end_year;
            drought_data_1{drought_data_index, 4} = end_hour_in_year;
            drought_data_1{drought_data_index, 5} = drought_events_1{i}.duration;
            drought_data_1{drought_data_index, 6} = drought_events_1{i}.lat;
            drought_data_1{drought_data_index, 7} = drought_events_1{i}.lon;
            drought_data_1{drought_data_index, 8} = drought_events_1{i}.condition;
            drought_data_1{drought_data_index, 9} = drought_events_1{i}.severity;
            drought_data_1{drought_data_index, 10} = drought_events_1{i}.intensity;
            drought_data_1{drought_data_index, 11} = drought_events_1{i}.YS;
            drought_data_index = drought_data_index + 1;
        end
    end
    
    drought_table_1 = cell2table(drought_data_1, 'VariableNames', {... 
        'Start_Year', 'Start_Hou', 'End_Year', 'End_Hou', ...
        'Duration', 'Lat', 'Lon', 'Condition', 'Severity', 'Intensity', 'YS'});
    writetable(drought_table_1, 'period1.csv');
end

if drought_count_2 > 0
    drought_data_2 = cell(drought_count_2, 11);
    drought_data_index = 1;
    
    for i = 1:drought_count_2
        start_year = floor((drought_events_2{i}.start_hou - 1) / 73) + 1980;
        start_hour_in_year = mod(drought_events_2{i}.start_hou - 1, 73) + 1;
        end_year = floor((drought_events_2{i}.end_hou - 1) / 73) + 1980;
        end_hour_in_year = mod(drought_events_2{i}.end_hou - 1, 73) + 1;
        
        if start_hour_in_year >= 19 && start_hour_in_year <= 55 && end_hour_in_year >= 19 && end_hour_in_year <= 55
            drought_data_2{drought_data_index, 1} = start_year;
            drought_data_2{drought_data_index, 2} = start_hour_in_year;
            drought_data_2{drought_data_index, 3} = end_year;
            drought_data_2{drought_data_index, 4} = end_hour_in_year;
            drought_data_2{drought_data_index, 5} = drought_events_2{i}.duration;
            drought_data_2{drought_data_index, 6} = drought_events_2{i}.lat;
            drought_data_2{drought_data_index, 7} = drought_events_2{i}.lon;
            drought_data_2{drought_data_index, 8} = drought_events_2{i}.condition;
            drought_data_2{drought_data_index, 9} = drought_events_2{i}.severity;
            drought_data_2{drought_data_index, 10} = drought_events_2{i}.intensity;
            drought_data_2{drought_data_index, 11} = drought_events_2{i}.YS;
            drought_data_index = drought_data_index + 1;
        end
    end
    
    drought_table_2 = cell2table(drought_data_2, 'VariableNames', {... 
        'Start_Year', 'Start_Hou', 'End_Year', 'End_Hou', ...
        'Duration', 'Lat', 'Lon', 'Condition', 'Severity', 'Intensity', 'YS'});
    writetable(drought_table_2, 'period2.csv');
end

drought_count = 0;
drought_events = {};
grid_drought_count = zeros(size(combined_data, 2), size(combined_data, 3));
grid_drought_duration = zeros(size(combined_data, 2), size(combined_data, 3));
grid_drought_severity = zeros(size(combined_data, 2), size(combined_data, 3));

for hou = 1:2993
    for lat_index = 1:size(combined_data, 2)
        for lon_index = 1:size(combined_data, 3)
            percentile = combined_data(hou, lat_index, lon_index);

            if percentile <= 20
                meet_condition = false;
                drought_condition = '';

                if combined_data(hou-1, lat_index, lon_index) >= 50
                    meet_condition = true;
                    drought_condition = 'one';
                elseif combined_data(hou-2, lat_index, lon_index) >= 50 && ( ...
                        combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index) >= 5) && ( ...
                        combined_data(hou-2, lat_index, lon_index) - combined_data(hou-1, lat_index, lon_index) >= 5)
                    meet_condition = true;
                    drought_condition = 'two';
                elseif combined_data(hou-3, lat_index, lon_index) >= 50 && ( ...
                        combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index) >= 5) && ( ...
                        combined_data(hou-2, lat_index, lon_index) - combined_data(hou-1, lat_index, lon_index) >= 5) && ( ...
                        combined_data(hou-3, lat_index, lon_index) - combined_data(hou-2, lat_index, lon_index) >= 5)
                    meet_condition = true;
                    drought_condition = 'three';
                elseif combined_data(hou-4, lat_index, lon_index) >= 50 && ( ...
                        combined_data(hou-1, lat_index, lon_index) - combined_data(hou, lat_index, lon_index) >= 5) && ( ...
                        combined_data(hou-2, lat_index, lon_index) - combined_data(hou-1, lat_index, lon_index) >= 5) && ( ...
                        combined_data(hou-3, lat_index, lon_index) - combined_data(hou-2, lat_index, lon_index) >= 5) && ( ...
                        combined_data(hou-4, lat_index, lon_index) - combined_data(hou-3, lat_index, lon_index) >= 5)
                    meet_condition = true;
                    drought_condition = 'four';
                end

                if meet_condition
                    drought_start_hou = hou;
                    drought_lat = lat_index;
                    drought_lon = lon_index;
                    drought_duration = 1;

                    for next_hou = hou+1:size(combined_data, 1)
                        next_percentile = combined_data(next_hou, lat_index, lon_index);
                        if next_percentile >= 20
                            drought_end_hou = next_hou;
                            drought_duration = drought_end_hou - drought_start_hou;

                            if drought_duration >= 3 && drought_duration < 12
                                drought_percentiles = combined_data(drought_start_hou:drought_end_hou, lat_index, lon_index);
                                ys_mask = drought_percentiles <= 20;
                                YS = sum(drought_percentiles(ys_mask));
                                
                                drought_count = drought_count + 1;
                                drought_events{drought_count}.start_hou = drought_start_hou;
                                drought_events{drought_count}.duration = drought_duration;
                                drought_events{drought_count}.end_hou = drought_end_hou;
                                drought_events{drought_count}.lat = drought_lat;
                                drought_events{drought_count}.lon = drought_lon;
                                drought_events{drought_count}.condition = drought_condition;
                                drought_events{drought_count}.severity = YS;

                                start_hour_in_year = mod(drought_start_hou - 1, 73) + 1;
                                end_hour_in_year = mod(drought_end_hou - 1, 73) + 1;
                                if start_hour_in_year >= 19 && start_hour_in_year <= 55 && end_hour_in_year >= 19 && end_hour_in_year <= 55
                                    grid_drought_count(lat_index, lon_index) = grid_drought_count(lat_index, lon_index) + 1;
                                    grid_drought_duration(lat_index, lon_index) = grid_drought_duration(lat_index, lon_index) + drought_duration;
                                    grid_drought_severity(lat_index, lon_index) = grid_drought_severity(lat_index, lon_index) + YS;
                                end
                            end
                            break;
                        end
                    end
                end
            end
        end
    end
end

grid_average_duration = zeros(size(combined_data, 2), size(combined_data, 3));
grid_average_severity = zeros(size(combined_data, 2), size(combined_data, 3));

nonzero_indices = grid_drought_count > 0;
if any(nonzero_indices(:))
    grid_average_duration(nonzero_indices) = grid_drought_duration(nonzero_indices) ./ grid_drought_count(nonzero_indices);
    grid_average_severity(nonzero_indices) = grid_drought_severity(nonzero_indices) ./ grid_drought_count(nonzero_indices);
end

save('drought_statistics.mat', ...
    'grid_drought_count', ...
    'grid_drought_duration', ...
    'grid_average_duration', ...
    'grid_drought_severity', ...
    'grid_average_severity', ...
    'drought_events', ...
    'drought_count');

================================

[original_data, R_orig] = readgeoraster('I:\DataArrangement\RawSoilMoisture\masked_SMroot_1980_0.tif');
info_orig = geotiffinfo('I:\DataArrangement\RawSoilMoisture\masked_SMroot_1980_0.tif');

grid_drought_count_flipped = flipud(grid_drought_count);
grid_average_duration_flipped = flipud(grid_average_duration);
grid_onset_rate_flipped = flipud(grid_average_severity);

grid_drought_count_flipped = fliplr(grid_drought_count_flipped);
grid_average_duration_flipped = fliplr(grid_average_duration_flipped);
grid_onset_rate_flipped = fliplr(grid_onset_rate_flipped);

grid_drought_count_rotated = rot90(grid_drought_count_flipped, 2);
grid_average_duration_rotated = rot90(grid_average_duration_flipped, 2);
grid_onset_rate_rotated = rot90(grid_onset_rate_flipped, 2);

nodata_value = NaN;
grid_drought_count_rotated(grid_drought_count_rotated == 0) = nodata_value;
grid_average_duration_rotated(grid_average_duration_rotated == 0) = nodata_value;
grid_onset_rate_rotated(grid_onset_rate_rotated == 0) = nodata_value;

R = R_orig;

geotiffwrite('frequency_1999_2020.tif', grid_drought_count_rotated, R, 'GeoKeyDirectoryTag', info_orig.GeoTIFFTags.GeoKeyDirectoryTag);
geotiffwrite('avg_duration_1999_2020.tif', grid_average_duration_rotated, R, 'GeoKeyDirectoryTag', info_orig.GeoTIFFTags.GeoKeyDirectoryTag);
geotiffwrite('avg_severity_1999_2020.tif', grid_onset_rate_rotated, R, 'GeoKeyDirectoryTag', info_orig.GeoTIFFTags.GeoKeyDirectoryTag);