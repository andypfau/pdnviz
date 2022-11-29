# allow Python to find our code library
from context import pdnviz


from pdnviz import PowerConfig, Load, Supply, DualLoad, LDO, DcDc, PowerGraph, PowerSpreadsheet


# Here we define some re-usable components as Pyton classes. Note
#   that the components also define thermal resistances and maximum
#   junction temperatures, which will also be evaluated by PDN Viz.

class LP2985_3V3(LDO):
    def __init__(self, name: str, v_in: float, **kwargs):
        super().__init__(
            name=name, v_in_nom=v_in,
            v_out=+3.3, i_out_max=0.15, i_gnd=1.8e-3, v_drop_min=0.35,
            r_th_ja=206, t_j_max=125,
            **kwargs)


class Reg113_5V0(LDO):
    def __init__(self, name: str, v_in: float, **kwargs):
        super().__init__(
            name=name, v_in_nom=v_in,
            v_out=+5.0, i_out_max=0.4, i_gnd=1e-3, v_drop_min=0.41,
            r_th_ja=160, t_j_max=125,
            **kwargs)


class LT3467_5V5(DcDc):
    def __init__(self, name: str, v_in: float, **kwargs):
        super().__init__(
            name=name, v_in_nom=v_in,
            v_out=+5.5, i_gnd=12e-6, eff_pct_over_i_out={1e-3:50,0.1:70,0.2:80}, i_out_max=1.1,
            r_th_ja=80, t_j_max=125,
            **kwargs)





if __name__ == '__main__':

    # define a global ambient temperature
    PowerConfig.t_ambient = +40

    # We define a more complex PDN, where several circuits are driven from
    #   a 5 V USB supply. Note that we put the components into groups (supply,
    #   analog, digital), and that we use converters that are defined as
    #   Python classes.

    G_SUPPLY = 'Supply'
    G_ANALOG = 'Analog'
    G_DIG = 'Digital'

    with Supply('USB +5V0USB', +5, i_out_max=0.5, group=G_SUPPLY) as pdn:
        
        p5v5 = pdn.add_sink(LT3467_5V5('SEPIC +5V5', v_in=+5, group=G_SUPPLY))
        p3v3d = p5v5.add_sink(LP2985_3V3('LDO +3V3D', v_in=+5.5, group=G_SUPPLY))
        p3v3a = p5v5.add_sink(LP2985_3V3('LDO +3V3A', v_in=+5.5, group=G_SUPPLY))
        p5v0a = p5v5.add_sink(Reg113_5V0('LDO +5V0A', v_in=+5.5, group=G_SUPPLY))

        I_PIC_OP_32MHz = 6.2e-3
        I_PIC_PLL = 0.7e-3
        I_PIC_USB = 4.4e-3
        I_PIC = I_PIC_OP_32MHz + I_PIC_PLL + I_PIC_USB
        p3v3d.add_sink(Load('PIC', v_in_nom=3.3, i_in=I_PIC, group=G_DIG))
        p3v3d.add_sink(Load('EEPROM', v_in_nom=3.3, i_in=3e-3, group=G_DIG))
        p3v3d.add_sink(Load('TempSens', v_in_nom=3.3, i_in=1e-3, group=G_DIG))
        p3v3d.add_sink(Load('RGB LED', v_in_nom=3.3, i_in=3*4e-3, group=G_DIG))
        p3v3d.add_sink(Load('XO', v_in_nom=3.3, i_in=4e-3, group=G_DIG))

        p3v3a.add_sink(Load('Reference', v_in_nom=3.3, i_in=1e-3, group=G_ANALOG))
        p5v0a.add_sink(Load('Buffer', v_in_nom=5, i_in=5e-3, group=G_ANALOG))
        p5v0a.add_sink(Load('Sensor', v_in_nom=5, i_in=0.113, group=G_ANALOG))

        adc = DualLoad('ADC', group=G_DIG,
            v_in_1_nom=3.3, in_1_name='Analog Supply In', i_in_1=1e-3,
            v_in_2_nom=3.3, in_2_name='Digital Supply In', i_in_2=1e-3)
        p3v3a.add_sink(adc.inputs[0])
        p3v3d.add_sink(adc.inputs[1])

    pdn.check()

    # Generate two spreadsheets: one with groups, one without groups (just to illustrate the feature)
    PowerSpreadsheet(pdn, grouped=False).save('./output/advanced_flat.xlsx', view=True)
    PowerSpreadsheet(pdn, grouped=True).save('./output/advanced_grouped.xlsx', view=True)
    
    # Generate a graph with groups
    PowerGraph(pdn, grouped=True, dissipation=False).save('./output/advanced.png', view=True)
