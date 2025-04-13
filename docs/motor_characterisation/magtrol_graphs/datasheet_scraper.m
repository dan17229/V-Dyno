% Magtrol Data Scraper
% Using Engauge Digitizer to extract info.
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

PB43 = fileloader("Pb43.csv");
WB43 = fileloader("Wb43.csv");
HD705 = fileloader("HD705.csv");
Drury = fileloader("ServoFromDrury.csv");

%Plotting the graphs
pat = ["-",":","-.","--"];
mark = ["+","o","s"];

% figure(1)
% hold on
% 
% % Plot the second line and shade the area under it
% x3 = HD705{:,1};
% y3 = HD705{:,2};
% a3 = area(x3, y3, 'FaceColor', 'k', 'FaceAlpha', 0.1, 'LineWidth', 2, 'LineStyle', pat(1));
% %p2 = plot(x2, y2, 'LineWidth', 2, 'LineStyle', pat(3), 'Color', 'k');
% 
% % Plot the first line and shade the area under it
% x1 = PB43{:,1};
% y1 = PB43{:,2};
% a1 = area(x1, y1, 'FaceColor', 'k', 'FaceAlpha', 0.1, 'LineWidth', 2, 'LineStyle', pat(3));
% %p1 = plot(x1, y1, 'LineWidth', 2, 'LineStyle', pat(1), 'Color', 'k');
% 
% % Plot the second line and shade the area under it
% x2 = WB43{:,1};
% y2 = WB43{:,2};
% a2 = area(x2, y2, 'FaceColor', 'k', 'FaceAlpha', 0.1, 'LineWidth', 2, 'LineStyle', pat(2));
% %p2 = plot(x2, y2, 'LineWidth', 2, 'LineStyle', pat(3), 'Color', 'k');
% 
% 
% xlabel("Rotational Speed (rpm)");
% ylabel("Torque (N\cdot{}m)");
% grid on
% grid minor
% %lgd = legend(["Hysteresis (HD705)","Powder Brake (2PB43)","Eddy-Current (2WB43)"],'Location','northeast',"box","off");
% %title(lgd,'Dynamometer Brake Technology')
% 
% xlim([10^0, 10^5])
% ylim([10^-2, 10^2])
% 
% % Set tick values and labels
% xticks([1, 10, 100, 1000, 10000, 100000])
% xticklabels({'1', '10', '100', '1000', '10,000', '100,000'})
% yticks([0.01, 0.1, 1, 10, 100])
% yticklabels({'0.01', '0.1', '1', '10', '100'})
% 
% % Set logarithmic scales
% set(gca, 'XScale', 'log')
% set(gca, 'YScale', 'log')
% 
% set(gca,'OuterPosition',[0 0 1.05 1]);
% scale=1;
% set(findall(gcf, 'type','text'),'fontsize',15*scale,'fontWeight','normal','FontName','Bitsream Charter')
% set(findall(gcf,'-property','FontSize'),'FontSize',15*scale,'fontWeight','normal','FontName','Bitsream Charter')
% set(findall(gcf, 'type','text'),'fontsize',12*scale,'fontWeight','normal','FontName','Bitsream Charter')
% set(findall(gcf,'-property','FontSize'),'FontSize',12*scale,'fontWeight','normal','FontName','Bitsream Charter')
% 
% hold off

%%%%% SECOND PLOT %%%%%

figure(2)
hold on

% Plot the second line and shade the area under it
x3 = Drury{:,1};
y3 = Drury{:,2};
a3 = area(x3, y3, 'FaceColor', 'k', 'FaceAlpha', 0.1, 'LineWidth', 2, 'LineStyle', pat(1));

% Plot the first line and shade the area under it
x1 = Drury{:,1};
y1 = Drury{:,3};
a1 = area(x1, y1, 'FaceColor', 'k', 'FaceAlpha', 0.1, 'LineWidth', 2, 'LineStyle', pat(3));

% Plot the first line and shade the area under it
x2 = Drury{:,1};
y2 = Drury{:,4};
a2 = area(x2, y2, 'FaceColor', 'k', 'FaceAlpha', .5, 'LineWidth', 2, 'LineStyle', pat(1));

xlabel("Rotational Speed, \omega (rpm)");
ylabel("Torque, \tau (N\cdot{}m)");
grid on
grid minor
%lgd = legend(["Hysteresis (HD705)","Powder Brake (2PB43)","Eddy-Current (2WB43)"],'Location','northeast',"box","off");
%title(lgd,'Dynamometer Brake Technology')

xline(4,Linewidth=2)
xline(8.5,Linewidth=2)

xlim([10^0, 10])
ylim([0, 10])

set(gca,'xtick',[])
set(gca,'xticklabel',[])
set(gca,'ytick',[])
set(gca,'yticklabel',[])

set(gca,'OuterPosition',[0 0 1.05 1]);
scale=1;
set(findall(gcf, 'type','text'),'fontsize',15*scale,'fontWeight','normal','FontName','Charter')
set(findall(gcf,'-property','FontSize'),'FontSize',15*scale,'fontWeight','normal','FontName','Charter')
set(findall(gcf, 'type','text'),'fontsize',12*scale,'fontWeight','normal','FontName','Charter')
set(findall(gcf,'-property','FontSize'),'FontSize',12*scale,'fontWeight','normal','FontName','Charter')

hold off