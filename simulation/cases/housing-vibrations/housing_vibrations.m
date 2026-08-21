clc;
close all;
clearvars;

% Ensure required package is available (Control Systems Toolbox for Octave)
if exist("pkg", "file")
  try
    pkg load control;
  catch
    error(["Required Octave package 'control' is not available.\n", ...
           "Install via: pkg install -forge control\n", ...
           "Then load via: pkg load control"]);
  end_try_catch
end

% Parameters (edit these)
v_feed = 5000 / 60 / 1000;            % m/s (feed speed)
r_min = 4e-3;                         % m (minimum corner radius)
m_stage = 30;                         % kg (mass of the stage)
a_stage = v_feed^2 / r_min;           % m/s² (stage acceleration)
m_housing = 10.0;                     % kg
m_base = 10.0;                        % kg
m_react = 0.1;                    % kg
k_housing = 1e6;                    % N/m  (ground <-> housing)
k_base = 10000e6;                       % N/m  (housing <-> base)
% k_base = 1e6 * m_stage * a_stage / 5e-3;    % N/m  (housing <-> base)
k_react = 20000e6;                      % N/m ((base <-> react)
%k_react = m_stage * a_stage / 5e-3;   % N/m ((base <-> react)

% Damping ratios (edit these)
eta_h = 0.2;         % damping ratio for ground <-> housing
eta_b = 1;         % damping ratio for housing <-> base
eta_r = 0.2;        % damping ratio for base <-> react

params = [m_housing, m_base, m_react, k_housing, k_base, k_react, eta_h, eta_b, eta_r];
if any(!isfinite(params)) || any(params <= 0)
  error("All parameters must be finite and > 0.");
end

% Coordinates:
% x_housing = displacement of housing mass relative to ground
% x_base    = displacement of base mass relative to ground
% x_react   = displacement of react mass relative to ground
%
% Equations (with damping):
% m_h * xh_ddot = -k_h*xh - c_h*xh_dot - k_b*(xh - xb) - c_b*(xh_dot - xb_dot)
% m_b * xb_ddot = -k_b*(xb - xh) - c_b*(xb_dot - xh_dot) - k_r*(xb - xr) - c_r*(xb_dot - xr_dot)
% m_r * xr_ddot = -k_r*(xr - xb) - c_r*(xr_dot - xb_dot) + F

mh = m_housing;
mb = m_base;
mr = m_react;
kh = k_housing;
kb = k_base;
kr = k_react;

% Viscous damping coefficients (derived from damping ratios)
% c_h uses the housing mass; internal dampers use reduced masses of relative modes.
m_eq_b = (mh * mb) / (mh + mb);
m_eq_r = (mb * mr) / (mb + mr);
c_h = eta_h * 2 * sqrt(kh * mh);
c_b = eta_b * 2 * sqrt(kb * m_eq_b);
c_r = eta_r * 2 * sqrt(kr * m_eq_r);

% State vector: [xh; xh_dot; xb; xb_dot; xr; xr_dot]
A = [ 0,              1,          0,          0,          0,      0;
     -(kh+kb)/mh, -(c_h+c_b)/mh,  kb/mh,   c_b/mh,       0,      0;
      0,              0,          0,          1,          0,      0;
      kb/mb,       c_b/mb,  -(kb+kr)/mb, -(c_b+c_r)/mb,  kr/mb,  c_r/mb;
      0,              0,          0,          0,          0,      1;
      0,              0,       kr/mr,     c_r/mr,    -kr/mr,  -c_r/mr ];

B = [0; 0; 0; 0; 0; 1/mr];            % input u = F (acts on m_react)
% outputs: y1 = x_housing, y2 = x_base, y3 = x_react
C = [1, 0, 0, 0, 0, 0;
     0, 0, 1, 0, 0, 0;
     0, 0, 0, 0, 1, 0];
D = [0;
     0;
     0];

sys = ss(A, B, C, D);
% Extract SISO subsystems (Octave's tf matrix indexing can be surprising)
sys_h = sys(1, :);               % x_housing / F
sys_b = sys(2, :);               % x_base / F
sys_r = sys(3, :);               % x_react / F
G_h = tf(sys_h);
G_b = tf(sys_b);
G_r = tf(sys_r);

disp("=== Three-mass spring system: [x_housing/F; x_base/F; x_react/F] ===");
disp("Parameters:");
printf("  m_housing = %.6g kg\n", mh);
printf("  m_base    = %.6g kg\n", mb);
printf("  m_react   = %.6g kg\n", mr);
printf("  k_housing = %.6g N/m\n", kh);
printf("  k_base    = %.6g N/m\n", kb);
printf("  k_react   = %.6g N/m\n", kr);
printf("  eta_h     = %.6g\n", eta_h);
printf("  eta_b     = %.6g\n", eta_b);
printf("  eta_r     = %.6g\n", eta_r);
printf("  c_h       = %.6g N*s/m\n", c_h);
printf("  c_b       = %.6g N*s/m\n", c_b);
printf("  c_r       = %.6g N*s/m\n", c_r);
disp("Transfer function G_h(s) = x_housing(s) / F(s):");
G_h
disp("Transfer function G_b(s) = x_base(s) / F(s):");
G_b
disp("Transfer function G_r(s) = x_react(s) / F(s):");
G_r

% Unit-step force input simulation (F = 1 N step)
t_end = 5.0;     % seconds
N = 2000;
t = linspace(0, t_end, N);

F_stage = m_stage * a_stage;
[y, t_out] = step(F_stage * sys, t);

figure("Name", "Step response: x_housing(t), x_base(t), x_react(t) for step force");
plot(t_out, y(:, 1) * 1000);
hold on;
plot(t_out, y(:, 2) * 1000);
plot(t_out, y(:, 3) * 1000);
hold off;
grid on;
xlabel("Time [s]");
ylabel("Displacement [mm]");
legend("x_{housing}", "x_{base}", "x_{react}", "Location", "northeast");
title(["Step input: F=",num2str(F_stage), " N on m_{react}"]);

% Impulse response (response to a momentary force F that accelerates the stage)
delta_t = r_min * pi / v_feed; % seconds (duration of cornering event)
dt = t(2) - t(1);
u = zeros(size(t));
pulse_samples = round(delta_t / dt);
u(1:pulse_samples) = F_stage * sin(2 * pi * t(1:pulse_samples) / (2 * delta_t));          % rectangular pulse
[y_lsim, t_lsim] = lsim(sys, u, t);

figure("Name", "Impulse response: x_housing(t), x_base(t), x_react(t) for impulse force");
plot(t_lsim, y_lsim(:, 1) * 1000);
hold on;
plot(t_lsim, y_lsim(:, 2) * 1000);
plot(t_lsim, y_lsim(:, 3) * 1000);
hold off;
grid on;
xlabel("Time [s]");
ylabel("Displacement [mm]");
legend("x_{housing}", "x_{base}", "x_{react}", "Location", "northeast");
title(["Impulse input scaled by F=",num2str(F_stage), " N on m_{react}"]);

% Bode plots of transfer functions
figure("Name", "Bode: x_housing/F");
bode(sys_h);
grid on;
title("Bode plot: x_{housing} / F");

figure("Name", "Bode: x_base/F");
bode(sys_b);
grid on;
title("Bode plot: x_{base} / F");

figure("Name", "Bode: x_react/F");
bode(sys_r);
grid on;
title("Bode plot: x_{react} / F");

