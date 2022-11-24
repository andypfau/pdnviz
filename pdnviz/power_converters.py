from .power_component import PowerComponent, PowerOutput, PowerInput
import logging
from scipy.interpolate import interp1d



class LDO(PowerComponent):
    

    def __init__(self, name: str, *, group: "str|None" = None,
                v_in_min: "float|None" = None, v_in_nom: "float|None" = None, v_in_max: "float|None" = None,
                v_drop_min: "float|None" = None, v_out: float, i_gnd: float = 0,
                i_out_max: "float|None" = None, p_diss_max: "float|None" = None,
                t_j_max: "float|None" = None, r_th_ja: "float|None" = None):
        self.input = PowerInput(parent = self, v_in_min=v_in_min, v_in_nom=v_in_nom, v_in_max=v_in_max, i_in=0)
        self.output = PowerOutput(parent = self, v_out=v_out, i_out_max=i_out_max)
        super().__init__(name, group=group, inputs=[self.input], outputs=[self.output], p_diss_max=p_diss_max,
            t_j_max=t_j_max, r_th_ja=r_th_ja)
        self.v_drop_min, self.i_gnd = v_drop_min, i_gnd
        self.v_drop_calc = None
    

    def __repr__(self) -> str:
        return f'<LDO({self.name})>'

    
    def _update_inputs(self):
        logging.debug(f'LDO({self.name})._update_inputs()')
        self.input.i_in = self.output.i_out_calc + self.i_gnd
        self.v_drop_calc = self.input.v_in_nom - self.output.v_out
        super()._update_inputs()
    
    
    def _check(self, raise_severe_errors: bool) -> bool:
        logging.debug(f'LDO({self.name})._check()')
        super()._check(raise_severe_errors)
        if self.input.v_in_nom is not None and self.v_drop_min is not None:
            if self.input.v_in_nom < self.v_drop_min:
                self._warn(f'Min. voltage drop exceeded')


class DcDc(PowerComponent):

    def __init__(self, name: str, *, group: "str|None" = None,
                v_in_min: "float|None" = None, v_in_nom: "float|None" = None, v_in_max: "float|None" = None,
                v_out: float, eff_pct_over_i_out: "dict[float,float]" = {}, i_gnd: float = 0,
                i_out_max: "float|None" = None, p_diss_max: "float|None" = None,
                t_j_max: "float|None" = None, r_th_ja: "float|None" = None):
        self.input = PowerInput(parent = self, v_in_min=v_in_min, v_in_nom=v_in_nom, v_in_max=v_in_max, i_in=0)
        self.output = PowerOutput(parent = self, v_out=v_out, i_out_max=i_out_max)
        super().__init__(name, group=group, inputs=[self.input], outputs=[self.output], p_diss_max=p_diss_max,
            t_j_max=t_j_max, r_th_ja=r_th_ja)
        self.eff_pct_over_i_out, self.i_gnd = eff_pct_over_i_out, i_gnd
    

    def __repr__(self) -> str:
        return f'<DcDc({self.name})>'


    def _update_inputs(self):
        logging.debug(f'DcDc({self.name})._update_conversion()')
        if len(self.eff_pct_over_i_out.keys()) > 0:
            intp = interp1d(x=list(self.eff_pct_over_i_out.keys()), y=list(self.eff_pct_over_i_out.values()), kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=False)
            self.eff_pct_calc = intp(self._outputs[0].i_out_calc)
        else:
            self.eff_pct_calc = 100
        self.output._update() # hack...
        p_in = self.output.p_out_calc / (self.eff_pct_calc/100)
        self.input.i_in = self.i_gnd + p_in / self._inputs[0].v_in_actual
        super()._update_inputs()
