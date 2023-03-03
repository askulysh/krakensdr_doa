import time

def tune(f1, f2, gain, web) :
    sp = web.module_signal_processor
    rec = web.module_signal_processor.module_receiver
    if gain == -1 :
        gain = rec.daq_rx_gain
    sampling_freq = rec.iq_header.sampling_freq
    center_freq = rec.daq_center_freq
    freq_low = center_freq - sampling_freq/2
    freq_high = center_freq + sampling_freq/2
    if f1 < freq_low or f2 > freq_high :
        center_freq = (f1+f2)/2
        if f1 == f2 :
            center_freq = center_freq + 50000
    if center_freq != rec.daq_center_freq or gain != rec.daq_rx_gain :
        print("Changing daq params")
        web.update_daq(float(center_freq)/10**6, gain)
        sp.active_vfos = 1
        sp.vfo_freq[0] = f1

    sp.data_ready = False
    while sp.data_ready == False :
        print("wait")
        time.sleep(0.05)

    return freq_low, freq_high

def MeasureTrace(args, web) :
    sp = web.module_signal_processor
    FreqStart_Hz = int(args[0])
    FreqStop_Hz = int(args[1])
    TraceType = int(args[2])
    TraceCount = int(args[3])
    PreAmp_dB = -1

    freq_low, freq_high = tune(FreqStart_Hz, FreqStop_Hz, PreAmp_dB, web)
    FrequencyStep_Hz = (freq_high-freq_low)/sp.spectrum_plot_size
    LevelMaxIndex = sp.spectrum_plot_size
    RBW_Hz = FrequencyStep_Hz
    TimeStamp = time.time()
    par = [     FrequencyStart_Hz,
                    FrequencyStep_Hz,
                    LevelMaxIndex,
                    TimeStamp,
                    RBW_Hz
          ]
    return par,sp.spectrum_plot_size, sp.spectrum[1]

def MeasureDF(args, web) :
    sp = web.module_signal_processor
    Freq_Hz = int(args[0])
    BearingCount = int(args[1])
    RBW_Hz = int(args[2])
    BW_Hz = int(args[3])
    PreAmp_dB = -1

    freq_low, freq_high = tune(Freq_Hz, Freq_Hz, PreAmp_dB, web)
    FrequencyStart_Hz = freq_low
    FrequencyStep_Hz = (freq_high-freq_low)/sp.spectrum_plot_size
    LevelMaxIndex = sp.spectrum_plot_size
    TimeStamp = time.time()
    PreAmp_dB = sp.module_receiver.daq_rx_gain
    RBW_Hz = FrequencyStep_Hz
    BearingAzimuth_deg = sp.bearing
    BearingWidth = sp.bearingWidth
    BearingSNR = sp.bearingSNR
    CompassAzimuth_deg = -1
    CompassElevation_deg = -1
    CompassRoll_deg = -1
    GnssLatitude_DEC = sp.latitude
    GnssLongitude_DEC = sp.longitude
    GnssAltitude_m = -1
    GnssSpeed_mps = - 1
    GnssCourse_deg = sp.heading

    par = [     FrequencyStart_Hz,
                FrequencyStep_Hz,
                LevelMaxIndex,
                RBW_Hz,
                BearingAzimuth_deg,
                BearingWidth,
                BearingSNR,

                CompassAzimuth_deg,
                CompassElevation_deg,
                CompassRoll_deg,

                GnssLatitude_DEC,
                GnssLongitude_DEC,
                GnssAltitude_m,
                GnssSpeed_mps,
                GnssCourse_deg,

                TimeStamp,
        ]
    return par,sp.spectrum_plot_size, sp.spectrum[1]

def run_command(cmd, args, web):
    if cmd != "DF" and cmd != "DF2" and cmd != "MeasureDF" and cmd != "MeasureTrace":
        print("Wrong command")
        raise ValueError("Wrong command")
        return

    sp = web.module_signal_processor
    print("Command: ", cmd, args)
    freq  = float(args[0])
#    gain = float(args[1])
    sampling_freq = sp.module_receiver.iq_header.sampling_freq
    center_freq = sp.module_receiver.daq_center_freq
    freq_low = center_freq - sampling_freq/2
    freq_high = center_freq + sampling_freq/2

    print(freq, sampling_freq, center_freq, freq_low, freq_high)

    if freq > freq_low and freq < freq_high :
        print("Set freq in current range")
        sp.vfo_freq[0] = freq
        if cmd == "DF2" :
            sp.vfo_freq[1] = float(args[1])
            sp.active_vfos = 2
        else:
            sp.active_vfos = 1
    elif freq != -1:
        print("Changing daq params")
        sp.data_ready  = False
        web.update_daq((freq+50000)/10**6,  sp.module_receiver.daq_rx_gain)
        sp.vfo_freq[0] = freq

    while sp.data_ready == False :
        print("wait")
        time.sleep(0.05)

    center_freq = sp.module_receiver.daq_center_freq
    freq_low = center_freq - sampling_freq/2

    FrequencyStart_Hz = freq_low
    FrequencyStep_Hz = sampling_freq/sp.spectrum_plot_size
    LevelMaxIndex = sp.spectrum_plot_size
    TimeStamp = time.time()
    RefLevel_dBm = -1
    Att_dB = -1
    PreAmp_dB = sp.module_receiver.daq_rx_gain
    RBW_Hz = -1
    DFBW_Hz = -1
    SweepTime_s = 0
    MeasTime_s = 0
    BearingAzimuth_deg = sp.doa_max_list[0]
    BearingAzimuthCorrection_deg = 0
    DFQuality_pc = -1
    BearingElevation_deg = -1

    CompassAzimuth_deg = -1
    MeasureCompassElevation_deg = -1
    CompassRoll_deg = -1

    Dispersion_degsq = -1

    if cmd == "DF":
        freq = -1
        if len(args) > 0:
            freq = int(args[0])
        if freq == -1 :
            freq = sp.vfo_freq[0]

        tune(freq, freq, -1, web)
        par = [sp.vfo_freq[0], sp.doa_max_list[0]]
        return par, sp.spectrum_plot_size, [1,1,1]
    elif cmd == "DF2":
        par = [sp.vfo_freq[0], sp.doa_max_list[0], sp.vfo_freq[1], sp.doa_max_list[1]]
        return par, sp.spectrum_plot_size, [1,1,1]

    elif cmd == "MeasureDF" :
        return MeasureDF(args, web)
    elif cmd == "MeasureTrace" :
        return MeasureTrace(args, web)

    return "error"
