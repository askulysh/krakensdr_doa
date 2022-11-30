import time

def run_command(cmd, args, web):
    if cmd != "DF" and cmd != "MeasureDF" and cmd != "MeasureTrace":
        print("Wrong command")
        raise ValueError("Wrong command")
        return

    sp = web.module_signal_processor
    print("Command: ", cmd, args)
    freq  = float(args[0])
    sampling_freq = sp.module_receiver.iq_header.sampling_freq
    center_freq = sp.module_receiver.daq_center_freq
    freq_low = center_freq - sampling_freq/2
    freq_high = center_freq + sampling_freq/2

    print(freq, sampling_freq, center_freq, freq_low, freq_high)

    if freq > freq_low and freq < freq_high :
        print("Set freq in current range")
        sp.vfo_freq[0] = freq
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

    GnssLatitude_DEC = -1
    GnssLongitude_DEC = -1
    GnssAltitude_m = -1
    GnssSpeed_mps = - 1
    GnssCourse_deg = -1

    Dispersion_degsq = -1

    if cmd == "DF":
        par = [sp.vfo_freq[0], sp.doa_max_list[0]]
        return par, sp.spectrum_plot_size, sp.spectrum[1]
    elif cmd == "MeasureDF" :
        par = [     FrequencyStart_Hz,
                    FrequencyStep_Hz,
                    LevelMaxIndex,
                    TimeStamp,
                    RefLevel_dBm,
                    Att_dB,
                    PreAmp_dB,
                    RBW_Hz,
                    DFBW_Hz,
                    SweepTime_s,
                    MeasTime_s,
                    BearingAzimuth_deg,
                    BearingAzimuthCorrection_deg,
                    DFQuality_pc,
                    BearingElevation_deg,

                    CompassAzimuth_deg,
                    MeasureCompassElevation_deg,
                    CompassRoll_deg,

                    GnssLatitude_DEC,
                    GnssLongitude_DEC,
                    GnssAltitude_m,
                    GnssSpeed_mps,
                    GnssCourse_deg,

                    Dispersion_degsq
               ]
        return par,sp.spectrum_plot_size, sp.spectrum[1]
    elif cmd == "MeasureTrace" :
        par = [     FrequencyStart_Hz,
                    FrequencyStep_Hz,
                    LevelMaxIndex,
                    TimeStamp,
                    RefLevel_dBm,
                    Att_dB,
                    PreAmp_dB,
                    RBW_Hz,
                    DFBW_Hz
              ]
        return par,sp.spectrum_plot_size, sp.spectrum[1]

    return "error"
