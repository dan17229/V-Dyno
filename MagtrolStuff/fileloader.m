function data = fileloader(name,scalingfactor)
    if nargin < 2
        scalingfactor = 1;
    end
    % Import data from CSV file
    opts = detectImportOptions(name);
    opts.VariableNamingRule = 'preserve';
    data = readtable(name, opts);
    columnNames = data.Properties.VariableNames;
    
    % Plot the original data and the new data
    for i = 2:length(columnNames) % Start from the second column
        data{:, i} = data{:, i}*scalingfactor; % Current column for y-axis
    end
    
end