from .power_component import PowerComponent, PowerOutput



class Supply(PowerComponent):

    def __init__(self, name: str, v_out: float, *, group: "str|None" = None,
            i_out_max: "float|None" = None, out_name: "str|None" = 'Supply Output', p_out_max: "float|None" = None):
        output = PowerOutput(name=out_name, parent=self, v_out=v_out, i_out_max=i_out_max)
        super().__init__(name, group=group, outputs=[output], p_out_max=p_out_max)
    

    def __repr__(self) -> str:
        return f'<Supply({self.name})>'



class MultiSupply(PowerComponent):

    def __init__(self, name: str, *, group: "str|None" = None,
            outputs: "list[PowerOutput]", p_out_total_max: "float|None" = None):
        self.outputs = outputs
        super().__init__(name, group=group, outputs=self.outputs, p_out_max=p_out_total_max)
    

    def __repr__(self) -> str:
        return f'<MultiSupply({self.name})>'



class DualSupply(MultiSupply):

    def __init__(self, name: str, *, group: "str|None" = None,
            v_out_1: float, i_out_1_max: "float|None" = None, p_out_1_max: "float|None" = None,
            v_out_2: float, i_out_2_max: "float|None" = None, p_out_2_max: "float|None" = None,
            out_1_name: "str|None" = 'Supply Output 1', out_2_name: "str|None" = 'Supply Output 2',
            p_out_total_max: "float|None" = None):
        out_1 = PowerOutput(name=out_1_name, parent = self, v_out=v_out_1, i_out_max=i_out_1_max, p_out_max=p_out_1_max)
        out_2 = PowerOutput(name=out_2_name, parent = self, v_out=v_out_2, i_out_max=i_out_2_max, p_out_max=p_out_2_max)
        super().__init__(name, group=group, outputs=[out_1, out_2], p_out_total_max=p_out_total_max)
    

    def __repr__(self) -> str:
        return f'<DualSupply({self.name})>'
