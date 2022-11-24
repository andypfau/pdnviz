import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pdnviz import Load, Supply, LDO, PowerGraph, PowerSpreadsheet


if __name__ == '__main__':
    
    # This is the same network as in example 2, but it will generate some errors:
    # - LDO 3.3 V expects a 5 V input voltage, but is connected to a 9 V source. This is an error in the network
    #     definition, and therefore will show as a Python warning. Note that you could turn this into an exception
    #     with the argument to the check() function further down.
    # - The maximum power dissipation of LDO 5.0 is exceeded, which will also generate a Python warning, but it
    #     will also show up in the spreadsheet.
    with Supply('Battery', +9, i_out_max=0.2) as battery:
        with battery.add_sink(LDO('LDO 5V', v_in_nom=+9, v_out=+5, i_out_max=0.09, p_diss_max=0.1)) as ldo3v3:
            ldo3v3.add_sink(Load('Sensor', v_in_nom=+5, i_in=60e-3))
        with battery.add_sink(LDO('LDO 3.3V', v_in_nom=+5, v_out=+3.3, i_out_max=0.1, p_diss_max=0.1)) as ldo5:
            ldo5.add_sink(Load('MCU', v_in_nom=+3.3, i_in=10e-3))
            ldo5.add_sink(Load('LED', v_in_nom=+3.3, i_in=2e-3))
            ldo5.add_sink(Load('Flash', v_in_nom=+3.3, i_in=4e-3))
    
    # You could turn the sever error (nominal voltage wrong) into an exception by passing <raise_severe_errors=True>.
    battery.check()

    PowerSpreadsheet(battery).save('./output/simple.xlsx', view=True)
