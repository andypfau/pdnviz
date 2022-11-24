import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pdnviz import Load, DualSupply, DualLoad, LDO, PowerGraph, PowerSpreadsheet


if __name__ == '__main__':
    
    # Define a PDN with multiple sources:
    #   Lab Supply +/- 12 V
    #     Motor +/- 12 V
    #     LDO 3.3V
    #       MCU
    #       LED (including resistor)
    #       ADC
    # Since we must have a single root element, the two power outputs that provide the +12 V and
    #   -12 V are inside a single DualSupply. We could also use a MultiSupply for arbitrarily 
    #   many sources.
    with DualSupply('Lab Supply', v_out_1=+5, v_out_2=-5) as supply:
        mot = DualLoad('Motor', v_in_1_nom=+5, v_in_2_nom=-5, i_in_1=1, i_in_2=1)
        supply.outputs[0].add_sink(mot.inputs[0])
        supply.outputs[1].add_sink(mot.inputs[1])
        with supply.outputs[0].add_sink(LDO('LDO 3.3V', v_in_nom=+5, v_out=+3.3, i_out_max=0.1, p_diss_max=0.15)) as ldo5:
            ldo5.add_sink(Load('MCU', v_in_nom=+3.3, i_in=10e-3))
            ldo5.add_sink(Load('LED', v_in_nom=+3.3, i_in=2e-3))
            ldo5.add_sink(Load('ADC', v_in_nom=+3.3, i_in=5e-3))
    
    supply.check()

    PowerSpreadsheet(supply).save('./output/multisource.xlsx', view=True)
    PowerGraph(supply, dissipation=True).save('./output/multisource.pdf', view=True)
