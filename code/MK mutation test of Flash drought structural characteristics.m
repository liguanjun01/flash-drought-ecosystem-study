clear; clc;

% ---------- Parameter Configuration -------------
dataFilePath = 'C:\Users\Yinyufei\Desktop\3.1\mk\data'; % Path to the data folder
resultPath = 'C:\Users\Yinyufei\Desktop\3.1\mk\result'; % Path to store results
excelSuffix = 'xlsx'; % Data file extension
limit = 1.96; % Threshold at 0.05 significance level is 1.96, 2.576 for 0.01 level
xstep = 5; % X-axis display step on the plot

% ---------- Start Calculation -------------
name0 = dir(cat(2, dataFilePath, '\', '*.', excelSuffix));
name = struct2cell(name0);
[w, l] = size(name);
U = {};

for k = 1:l
    disp(cat(2, name{1,k}, ' calculating...'))
    A = xlsread(cat(2, dataFilePath, '\', name{1,k})); % Read data from Excel
    x = A(:,1); % Time data
    y = A(:,2); % Meteorological factor data
    n = length(y); % Data length
    
    Sk = zeros(size(y));
    UF = zeros(size(y));
    s = 0;
    for i = 2:n
        for j = 1:i
            if y(i) > y(j)
                s = s + 1;
            else
                s = s + 0;
            end
        end
        Sk(i) = s; % Rank series
        E = i * (i - 1) / 4; % Mean
        Var = i * (i - 1) * (2 * i + 5) / 72; % Variance
        UF(i) = (Sk(i) - E) / sqrt(Var);
    end
    
    y2 = zeros(size(y));
    Sk2 = zeros(size(y));
    UB = zeros(size(y));
    s = 0;
    for i = 1:n
        y2(i) = y(n - i + 1); % Reverse the sequence for recalculation
    end
    for i = 2:n
        for j = 1:i
            if y2(i) > y2(j)
                s = s + 1;
            else
                s = s + 0;
            end
        end
        Sk2(i) = s; % Rank series
        E = i * (i - 1) / 4; % Mean
        Var = i * (i - 1) * (2 * i + 5) / 72; % Variance
        UB(i) = 0 - (Sk2(i) - E) / sqrt(Var);
    end
    
    UB2 = zeros(size(y));
    for i = 1:n
        UB2(i) = UB(n - i + 1); % Reverse the result back
    end
    
    % ---------- Write Results to Excel -------------
    if strcmp(excelSuffix, 'xls')
        suffixNum = 4;
    else
        suffixNum = 5;
    end
    
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), x, 1, 'A2');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), UF, 1, 'B2');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), UB2, 1, 'C2');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), -limit * ones(n,1), 1, 'D2');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), limit * ones(n,1), 1, 'E2');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), {'Time'}, 1, 'A1');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), {'UF'}, 1, 'B1');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), {'UB'}, 1, 'C1');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), {'Lower_Limit'}, 1, 'D1');
    xlswrite(cat(2, resultPath, '\', name{1,k}(1:end-suffixNum), '_MK_Statistics.xlsx'), {'Upper_Limit'}, 1, 'E1');
    
    % ---------- Plotting -------------
    figure(k)
    plot(x, UF, 'r-', 'linewidth', 1.5); % Plot UF curve
    hold on
    plot(x, UB2, 'b-.', 'linewidth', 1.5); % Plot UB curve
    plot(x, limit * ones(n,1), 'k:', 'linewidth', 1); % Upper limit
    plot(x, -limit * ones(n,1), 'k:', 'linewidth', 1); % Lower limit
    plot(x, 0 * ones(n,1), '-.', 'linewidth', 1); % Zero line
    
    tickv = x(1):xstep:x(n); % Set step
    set(gca, 'XTick', tickv);
    set(gca, 'XTickMode', 'manual');
    set(gca, 'XTickLabelMode', 'manual');
    tickstr = num2str((x(1):xstep:x(n)).');
    set(gca, 'XTickLabel', tickstr);
    set(gca, 'XMinorTick', 'on')
    legend('UF', 'UB', '0.05 Significance Level'); % Set legend
    xlabel('Year', 'FontName', 'TimesNewRoman', 'FontSize', 12); % X-axis label
    ylabel('MK Statistic', 'FontName', 'TimesNewRoman', 'Fontsize', 12); % Y-axis label
    print(gcf, '-dbitmap', cat(2, resultPath, '\', name{1,k}(1:end-4), '.bmp')); % Save image
end 

close all;
disp('Calculation completed!')
