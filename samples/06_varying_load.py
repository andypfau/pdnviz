# allow Python to find our code library
from context import pdnviz


from pdnviz import Load, Supply, LDO, PowerSpreadsheet, PowerComponent


if __name__ == '__main__':

    # This circuit has two stepper motors, which each draw a certain current, but the supply cannot provide
    #   enough power for both at once. By sweeping all combinations, we will find out which combinations work,
    #   and which don't.

    for idx_xaxis, i_xaxis in enumerate([0, 0.8]):
        for idx_yaxis, i_yaxis in enumerate([0, 0.8]):

            # We will re-define the circuit several times. To avoid warnings about duplicate names, we first
            #   clear the list of known names. We could instead just as well define the circuit once (outside
            #   of the loop), and inside of the loop we could overwrite i_in of the two loads.
            PowerComponent.clear_names()
            
            with Supply('Supply', +12, i_out_max=1.5) as supply:
                supply.add_sink(Load('X-Axis Stepper', v_in_nom=+12, i_in=i_xaxis))
                supply.add_sink(Load('Y-Axis Stepper', v_in_nom=+12, i_in=i_yaxis))
                with supply.add_sink(LDO('LDO 3.3V', v_in_nom=+12, v_out=+3.3, i_out_max=0.1, p_diss_max=0.25)) as ldo5:
                    ldo5.add_sink(Load('MCU', v_in_nom=+3.3, i_in=10e-3))
                    ldo5.add_sink(Load('X-Axis Driver', v_in_nom=+3.3, i_in=5e-3))
                    ldo5.add_sink(Load('Y-Axis Driver', v_in_nom=+3.3, i_in=5e-3))
            
            supply.check()
            PowerSpreadsheet(supply).save(f'./output/varying_load_x{idx_xaxis}y{idx_yaxis}.xlsx')
None