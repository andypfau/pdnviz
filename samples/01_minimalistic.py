import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pdnviz import Load, Supply, PowerSpreadsheet


if __name__ == '__main__':
    
    # Define a minimalistic PDN (power distribution network):
    #   12 V / 3A Supply -> Motor, 1 A
    # Notice that the sink (the motor) explicitly defines a nominal voltage (12 V); this allows the
    #   tool to automatically check for wiring errors. Also, since the maximum output current of
    #   the source is known, as well as the input current of the sink, the source can be checked
    #   for overload.
    with Supply('Supply', +12, i_out_max=3) as supply:
        supply.add_sink(Load('Motor', v_in_nom=+12, i_in=1))
    
    # Note that <supply> is the "root element" of this PDN (it is the entity that produces power)
    #   for the whole PDN), and therefore all future operations are done on that object.
    
    # This updates the PDN, and checks for errors.
    # This must be called explicitly, otherwise you might get meaningless intermediate warnings or errors.
    supply.check()

    # output as spreadsheet
    PowerSpreadsheet(supply).save('./output/minimalistic.xlsx', view=True)
