% Load Motor Brake data
MotorBrake = fileloader("MotorBrake.csv");

% Define line styles
pat = ["-",":","-.","--"];

figure(1)
hold on

% Plot Motor Brake data and shade the area under the curve
x = MotorBrake{:,1};  % Rotational speed (rpm)
y = MotorBrake{:,2};  % Torque (N·m)
a = area(x, y, 'FaceColor', 'k', 'FaceAlpha', 0.2, 'LineWidth', 2, 'LineStyle', pat(1)); % Blue shading

% Set axis labels
xlabel("Rotational Speed (rpm)");
ylabel("Torque (N·m)");

% Enable grid
grid on
grid minor

% Set legend
lgd = legend(["Motor Brake"], 'Location', 'northeast', "box", "off");
title(lgd, 'Dynamometer Motor Brake ')

% Set logarithmic scales
xlim([10^0, 10^5])
ylim([10^-2, 10^3])
set(gca, 'XScale', 'log')
set(gca, 'YScale', 'log')

% Customize tick labels for better readability
xticks([1, 10, 100, 1000, 10000, 100000])
xticklabels({'1', '10', '100', '1,000', '10,000', '100,000'})

yticks([0.01, 0.1, 1, 10, 100, 1000])
yticklabels({'0.01', '0.1', '1', '10', '100', '1,000'})

% Improve figure layout and fonts
set(gca, 'OuterPosition', [0 0 1.05 1]);
scale = 1;
set(findall(gcf, 'type','text'), 'fontsize', 15*scale, 'fontWeight', 'normal', 'FontName', 'Bitstream Charter')
set(findall(gcf, '-property', 'FontSize'), 'FontSize', 15*scale, 'fontWeight', 'normal', 'FontName', 'Bitstream Charter')

hold off