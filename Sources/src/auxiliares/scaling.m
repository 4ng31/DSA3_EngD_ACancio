%
% PWELCH SCALING TEST
%
% FINDINGS: x1 and x2 are of different durations. x2 is longer than x1.
% Pxx2 will be proportially larger than Pxx1 (if x2 is twice as long as x1,
% Pxx2 will be twice as large as Pxx1). However, if window length in
% pwelch is set to the same value for both x1 and x2, Pxx1=Pxx2. However,
% in both cases, Pxx1 and Pxx2 are not equal to signal power (amplitude of
% x1 or x2 squared). Amplitude normalization is required. When hanning
% window is used, the correction is 1.5*Pxx. (1.5=4/(8/3). 8/3 for window
% and 4 for discrete signal). pwelch appears to apply a broadband/random
% window correction factor. This means that the amplitude of a discrete
% sinusoidal will not be correct, but it can be corrected for by the ratio
% of the discrete signal correction factor over the random broadband/random
% factor.
%
% PWELCH Scaling Factor with Hanning Window: sqrt(2*Pxx*1.5). It
% correspondsto signal amplitude. If no window (rectwin), then no 1.5
% factor is needed. Just use sqrt(2*Pxx).
%
Fs=128;
t1=0:1/Fs:2-1/Fs;A1=1;
t2=0:1/Fs:4-1/Fs;A2=1;
x1=A1*cos(2*pi*20*t1);RMS1=A1/sqrt(2); %RMS voltage
fprintf(1,'Vrms1=%f\n',RMS1);
x2=A2*cos(2*pi*20*t2);RMS2=A2/sqrt(2); %RMS voltage
fprintf(1,'Vrms2=%f\n',RMS2);
%
N1=length(x1);
N2=length(x2);
%
[Pxx1,F1] = pwelch(x1,hanning(N1/2),0,N1/2,Fs);Prms1=sqrt(max(Pxx1)*1.5);
[Pxx2,F2] = pwelch(x2,hanning(N1/2),0,N1/2,Fs);Prms2=sqrt(max(Pxx2)*1.5);
%
fprintf(1,'Prms1=%f\n',Prms1);
fprintf(1,'Prms2=%f\n',Prms2);
%
figure(1);
subplot(2,1,1);plot(F1,sqrt(Pxx1*1.5));grid on;%ylim([0 1]); %RMS power
subplot(2,1,2);plot(F2,sqrt(Pxx2*1.5));grid on;%ylim([0 1]); %RMS power
%
figure(2)
subplot(2,1,1);plot(F1,sqrt(2*Pxx1*1.5));grid on;%ylim([0 1]); %Voltage Amplitude
subplot(2,1,2);plot(F2,sqrt(2*Pxx2*1.5));grid on;%ylim([0 1]); %Voltage Amplitude 