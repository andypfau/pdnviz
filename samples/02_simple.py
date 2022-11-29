# allow Python to find our code library
from context import pdnviz


from pdnviz import Load, Supply, LDO, PowerGraph, PowerSpreadsheet


if __name__ == '__main__':
    
    # Define a simple PDN:
    #   Battery 9 V
    #     LDO 5V
    #       Sensor
    #     LDO 3.3 V
    #       MCU
    #       LED (including resistor)
    #       Flash memory
    # Note that this time we also define a maximum power dissipation for the LDOs
    with Supply('Battery', +9, i_out_max=0.2) as battery:
        with battery.add_sink(LDO('LDO 5V', v_in_nom=+9, v_out=+5, i_out_max=0.09, p_diss_max=0.1)) as ldo3v3:
            ldo3v3.add_sink(Load('Sensor', v_in_nom=+5, i_in=6e-3))
        with battery.add_sink(LDO('LDO 3.3V', v_in_nom=+9, v_out=+3.3, i_out_max=0.1, p_diss_max=0.15)) as ldo5:
            ldo5.add_sink(Load('MCU', v_in_nom=+3.3, i_in=10e-3))
            ldo5.add_sink(Load('LED', v_in_nom=+3.3, i_in=2e-3))
            ldo5.add_sink(Load('Flash', v_in_nom=+3.3, i_in=4e-3))
    battery.check()

    PowerSpreadsheet(battery).save('./output/simple.xlsx', view=True)

    # Also generate a graph of the network
    # <dissipation=True> means that additional arrows show dissipated heat of each component.
    # Note that we could have used a different format as well, e.g. PDF
    PowerGraph(battery, dissipation=True).save('./output/simple.png', view=True)
