from .power_component import PowerComponent, PowerInput



class Load(PowerComponent):

    def __init__(self, name: str, *, group: "str|None" = None,
            v_in_min: "float|None" = None, v_in_nom: "float|None" = 'Supply Input', v_in_max: "float|None" = None,
            in_name: "str|None" = None, i_in: float = 0, p_diss_max: "float|None" = None):
        input = PowerInput(name=in_name, parent = self, v_in_min=v_in_min, v_in_nom=v_in_nom, v_in_max=v_in_max, i_in=i_in)
        super().__init__(name, group=group, inputs=[input], p_diss_max=p_diss_max)
    

    def __repr__(self) -> str:
        return f'<Load({self.name})>'



class MultiLoad(PowerComponent):

    def __init__(self, name: str, *, group: "str|None" = None,
            inputs: "list[PowerInput]", p_diss_max: "float|None" = None):
        self.inputs = inputs
        super().__init__(name, group=group, inputs=self.inputs, p_diss_max=p_diss_max)
    

    def __repr__(self) -> str:
        return f'<MultiLoad({self.name})>'



class DualLoad(MultiLoad):

    def __init__(self, name: str, *, group: "str|None" = None,
            v_in_1_min: "float|None" = None, v_in_1_nom: "float|None" = None, v_in_1_max: "float|None" = None,
            v_in_2_min: "float|None" = None, v_in_2_nom: "float|None" = None, v_in_2_max: "float|None" = None,
            i_in_1: float = 0, i_in_2: float = 0,
            in_1_name: "str|None" = 'Supply Input 1', in_2_name: "str|None" = 'Supply Input 2',
            p_diss_max: "float|None" = None):
        in_1 = PowerInput(name=in_1_name, parent = self, v_in_min=v_in_1_min, v_in_nom=v_in_1_nom, v_in_max=v_in_1_max, i_in=i_in_1)
        in_2 = PowerInput(name=in_2_name, parent = self, v_in_min=v_in_2_min, v_in_nom=v_in_2_nom, v_in_max=v_in_2_max, i_in=i_in_2)
        super().__init__(name, group=group, inputs=[in_1, in_2], p_diss_max=p_diss_max)
    

    def __repr__(self) -> str:
        return f'<DualLoad({self.name})>'
