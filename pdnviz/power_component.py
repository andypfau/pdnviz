from .power_base import PowerBaseElement, PowerConfig
import logging, warnings
from dataclasses import dataclass



@dataclass
class PowerHierarchy:
    
    """The name of the group, or Ellipsis (...) if the data is not grouped"""
    group: "str|Ellipsis"
    
    """List of sources that provide power into this PDN hierarchy (for the given group only)"""
    sources: "list[GroupSource]"
    
    """The hierarchy of connected loads (for the given group only).
    Use this to determine how the power is distributed though the network. Do not use this to sum up the dissipated power,
    as e.g. components with multiple inputs or outputs might appear multiple times in the hierarchy."""
    sink_hierarchy: "list[PowerHierarchyElement]"
    
    """List of all components that dissipate power (for the given group only).
    Since every component appears exactly once in this list, and pure sources are excluded, you can use this to evaluate the dissipated power."""
    all_dissipating_components: "list[PowerComponent]"
    
    """A list of sources, within this group, that provide power to other groups. If the data is not grouped,
    this list is always empty."""
    to_external: "list[GroupSourceToExternal]"



@dataclass
class GroupSource:
    
    """The output that drives power"""
    output: "PowerOutput"
    
    """The current that is drawn by the given group.
    If the data is not grouped, this is equal to the current reported by the output."""
    i_drawn: float
    
    """The power that is drawn by the given group.
    If the data is not grouped, this is equal to the power reported by the output."""
    p_drawn: float



@dataclass
class GroupSourceToExternal:
    
    """The output that drives power"""
    output: "PowerOutput"

    """List of groups that receive power from this source"""
    receiving_groups: list[str]
    
    """The current that is supplied to other groups"""
    i_provided: float
    
    """The power that is supplied to other groups"""
    p_provided: float



@dataclass
class PowerHierarchyElement:
    
    """The input that comes next"""
    input: "PowerInput"
    
    """Any sinks within this group that in turn draw power from this component"""
    connected_sinks: "list[PowerHierarchyElement]"



class PowerComponent(PowerBaseElement):


    _names: "list[str]" = []


    def __init__(self, name: str, *, group: "str|None" = None,
                 inputs: "list[PowerInput]" = [], outputs: "list[PowerOutput]" = [],
                 p_out_max: "float|None" = None, p_diss_max: "float|None" = None,
                 t_j_max: "float|None" = None, r_th_ja: "float|None" = None):
        super().__init__(name)
        if name in PowerComponent._names:
            warnings.warn(f'Duplicate name "{name}"')
        PowerComponent._names.append(name)
        self.name, self.group, self._inputs, self._outputs, self.p_out_max, self.p_diss_max = name, group, inputs, outputs, p_out_max, p_diss_max
        self.t_j_max, self.r_th_ja = t_j_max, r_th_ja
        self.p_in_calc, self.p_diss_calc, self.p_out_calc, self.t_j_calc = None, None, None, None
    

    def __repr__(self) -> str:
        return f'<PowerComponent({self.name})>'

    
    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    

    def _get_input(self) -> "PowerInput":
        if len(self._inputs) != 1:
            raise RuntimeError(f'Component <{self.name}> does not have a single unique input')
        return self._inputs[0]


    def _get_output(self) -> "PowerOutput":
        if len(self._outputs) != 1:
            raise RuntimeError(f'Component <{self.name}> does not have a single unique output')
        return self._outputs[0]
    

    @staticmethod
    def clear_names():
        """Call this before you want to re-define a network; otherwise you will get errors about duplicate names"""
        PowerComponent._names = []
    

    def add_sink(self, sink: "PowerComponent|PowerInput", source: "PowerOutput|None" = None) -> "PowerComponent|PowerInput":
        if isinstance(sink, PowerInput):
            input = sink
        elif isinstance(sink, PowerComponent):
            input = sink._get_input()
        else:
            raise TypeError()
        if isinstance(source, PowerOutput):
            output = source
        elif source is None:
            output = self._get_output()
        else:
            raise TypeError()
        output.add_sink(input)
        return sink
    

    def _verify_names(self):
        logging.debug(f'Component({self.name})._verify_names()')
        input_names = [i.name for i in self._inputs]
        if len(input_names) != len(set(input_names)):
            raise RuntimeError(f'Component <{self.name}> has duplicate input names')
        output_names = [o.name for o in self._outputs]
        if len(output_names) != len(set(output_names)):
            raise RuntimeError(f'Component <{self.name}> has duplicate output names')


    def _update_downstream_components(self):
        logging.debug(f'Component({self.name})._update_tree()')
        for output in self._outputs:
            for downstream_input in output._sinks:
                downstream_input.parent.update()

    
    def _pre_update(self):
        for output in self._outputs:
            output._pre_update()
        for input in self._inputs:
            input._pre_update()
    
    
    def _update_outputs(self):
        for output in self._outputs:
            output._update()
    
    
    def _update_inputs(self):
        for input in self._inputs:
            input._update()

    
    def _update_power(self):
        logging.debug(f'Component({self.name})._update_power()')
        self.p_in_calc = sum([i.p_in_calc for i in self._inputs])
        self.p_out_calc = sum([o.p_out_calc for o in self._outputs])
        self.p_diss_calc = self.p_in_calc - self.p_out_calc

    
    def _update_thermal(self):
        logging.debug(f'Component({self.name})._update_thermal()')
        self.t_j_calc = PowerConfig.t_ambient
        if self.r_th_ja is not None:
            self.t_j_calc += self.p_diss_calc * self.r_th_ja


    def update(self):
        logging.debug(f'Component({self.name}).update()')
        self._update_downstream_components()
        self._verify_names()
        self._pre_update()
        self._update_outputs()
        self._update_inputs()
        self._update_power()
        self._update_thermal()


    def _check_tree(self, raise_severe_errors: bool):
        logging.debug(f'Component({self.name})._check_tree()')
        if len(self._inputs)==0 and len(self._outputs)==0:
            self._warn(f'This component has no inputs and no outputs')
        for output in self._outputs:
            for downstream_input in output._sinks:
                downstream_input.parent._check_tree(raise_severe_errors)
                downstream_input._check(raise_severe_errors)
            output._check(raise_severe_errors)
        self._check(raise_severe_errors)

    
    def _check(self, raise_severe_errors: bool):
        logging.debug(f'Component({self.name})._check()')
        if self.p_out_max is not None:
            if self.p_out_calc > self.p_out_max:
                self._warn(f'Max. output power exceeded')
        if self.p_diss_max is not None:
            if self.p_diss_calc > self.p_diss_max:
                self._warn(f'Max. dissipated power exceeded')
        if self.r_th_ja is not None and self.t_j_calc is not None:
            if self.t_j_calc > self.t_j_max:
                self._warn(f'Max. junction temperature exceeded')


    def check(self, raise_severe_errors: bool = False) -> bool:
        logging.debug(f'Component({self.name}).check()')
        self.update()
        self.clear_warnings()
        self._check_tree(raise_severe_errors)
        return self.ok()
    

    def _print_tree(self, indent: int):
        print(f'{"  "*indent}{self.name}: {self.p_diss_calc:.5g} W')
        for i in self._inputs:
            print(f'{"  "*indent}  Input {i.name}: {i.v_in_actual:.5g} V, {i.i_in:.5g} A')
        for o in self._outputs:
            print(f'{"  "*indent}  Output {o.name}: {o.v_out:.5g} V, {o.i_out_calc:.5g} A')
            for downstream_input in o._sinks:
                downstream_input.parent._print_tree(indent+2)
    

    def print_tree(self):
        self.update()
        self._print_tree(0)


    def get_hierarchy(self, grouped: bool = False) -> "list[PowerHierarchy]":
        
        if grouped:
            groups = { g: self.get_all_components(g) for g in self.get_all_groups() }
        else:
            groups = { Ellipsis: self.get_all_components() }
        
        result = []
        for group, components in groups.items():
            
            sources = self._find_sources(components)

            group_sources = []
            for source in sources:
                if grouped:
                    i, p = 0, 0
                    for sink in source._sinks:
                        if sink.parent.group == group:
                            i += sink.i_in
                            p += sink.p_in_calc
                else:
                    i, p = source.i_out_calc, source.p_out_calc
                group_sources.append(GroupSource(source, i, p))
            
            def recurse(sinks: "list[PowerInput]") -> list[PowerHierarchyElement]:
                result = []
                for sink in set(sinks):
                    downsteram_sources = self._find_downstream_sources([sink])
                    downstream_sinks = self._find_sinks_connected_to(downsteram_sources, components)
                    if len(downstream_sinks) > 0:
                        connected_sinks = recurse(downstream_sinks)
                    else:
                        connected_sinks = []
                    result.append(PowerHierarchyElement(sink, connected_sinks))
                return result
            hierarchy = recurse(self._find_sinks_connected_to(sources, components))

            dissipating_components = list(set([c for c in components if not c.is_pure_source()]))
            
            to_external = []
            receivers = set()
            if grouped:
                for source in self._find_local_supplies_to_external(components):
                    i, p = 0, 0
                    for sink in source._sinks:
                        if sink.parent.group != group:
                            i += sink.i_in
                            p += sink.p_in_calc
                            receivers.add(sink.parent.group)
                    to_external.append(GroupSourceToExternal(source, list(receivers), i, p))
            
            result.append(PowerHierarchy(group, group_sources, hierarchy, dissipating_components, to_external))
        return result
    

    def get_all(self) -> "tuple[list[PowerComponent],list[str]]":
        return (self.get_all_components(), self.get_all_groups())
        

    def get_all_groups(self) -> "list[str]":
        return list(set([c.group for c in self.get_all_components()]))
    

    def get_all_components(self, group: "str|Ellipsis" = ...) -> "list[PowerComponent]":
        self.update()
        result = []
        for output in self._outputs:
            for downstream_input in output._sinks:
                result.extend(downstream_input.parent.get_all_components())
        result.append(self)
        if group is not ...:
            result = [c for c in result if c.group == group]
        return result
    

    @staticmethod
    def _find_sources(components: "list[PowerComponent]") -> "list[PowerOutput]":
        """
        Returns all outputs that provide power to the given list of components.
        This only includes outputs that are either not in <components> itself (i.e.
        that come from the outside), or outputs of pure supplies (not converters).
        """
        outputs = []
        for component in components:
            for input in component._inputs:
                driving_output = input.source
                source_is_pure_supply = driving_output.parent.is_pure_source()
                source_is_external = driving_output.parent not in components
                if source_is_pure_supply or source_is_external:
                    if driving_output not in outputs:
                        outputs.append(driving_output)
        return outputs



    @staticmethod
    def _find_downstream_sources(sinks: "list[PowerInput]") -> "list[PowerOutput]":
        outputs = []
        for sink in sinks:
            outputs.extend(sink.parent._outputs)
        return outputs


    @staticmethod
    def _find_sinks_connected_to(sources: "list[PowerOutput]", components: "list[PowerComponent]") -> "list[PowerInput]":
        """Returns all inputs that are connected to the given output in the given list of components"""
        inputs = []
        for component in components:
            for input in component._inputs:
                if input.source in sources:
                    if input not in inputs:
                        inputs.append(input)
        return inputs


    @staticmethod
    def _find_local_supplies_to_external(components: "list[PowerComponent]") -> "list[PowerOutput]":
        """Returns all outputs that provide power to components that are not in the given list"""
        outputs = []
        for component in components:
            for output in component._outputs:
                include = False
                for input in output._sinks:
                    if input.parent not in components:
                        include = True
                        break
                if include and output not in outputs:
                    outputs.append(output)
        return outputs
    
    
    def is_pure_source(self) -> bool:
        """Returns True if this component has outputs, but no inputs"""
        return len(self._inputs)==0 and len(self._outputs)>0
    
    
    def is_pure_sink(self) -> bool:
        """Returns True if this component has inputs, but no outputs"""
        return len(self._inputs)>0 and len(self._outputs)==0
    
    
    def is_converter(self) -> bool:
        """Returns True if this component has both inputs and outputs"""
        return len(self._inputs)>0 and len(self._outputs)>0



class PowerInput(PowerBaseElement):


    def __init__(self, *, parent: "PowerComponent", name: "str|None" = None, v_in_min: "float|None" = None,
        v_in_nom: "float|None" = None, v_in_max: "float|None" = None, i_in: float = 0):
        if name is None:
            if v_in_nom is None:
                raise ValueError('Must specify either a name or a nominal input voltage')
            name = f'{v_in_nom:.3g} V In'
        super().__init__(name)
        self.parent = parent
        self.v_in_min, self.v_in_nom, self.v_in_max, self.i_in = v_in_min, v_in_nom, v_in_max, i_in
        self.v_in_actual, self.p_in_calc = None, None
        self.source = None # type: PowerOutput
    

    def __repr__(self) -> str:
        return f'<PowerInput({self.full_name()})>'
    

    def _set_source(self, source: "PowerOutput"):
        if self.source is not None and self.source != source:
            raise RuntimeError('Cannot re-assign a different source')
        logging.debug(f'Input({self.full_name()}) is now connected to Output({source.full_name()})')
        self.source = source


    def _pre_update(self):
        logging.debug(f'Input({self.full_name()})._pre_update()')
        self.v_in_actual = self.source.v_out


    def _update(self):
        logging.debug(f'Input({self.full_name()})._update()')
        self.p_in_calc = abs(self.v_in_actual * self.i_in)


    def _check(self, raise_severe_errors: bool) -> bool:
        logging.debug(f'Input({self.full_name()})._check()')
        if self.v_in_min is not None:
            if self.source.v_out < self.v_in_min:
                self._warn(f'Min. input voltage exceeded')
        if self.v_in_max is not None:
            if self.source.v_out > self.v_in_max:
                self._warn(f'Max. input voltage exceeded')
        if self.v_in_min is None and self.v_in_max is None and self.v_in_nom is not None:
            if self.source.v_out != self.v_in_nom:
                self._warn(f'Nom. input voltage violated', raise_severe_errors)
        return self.ok()
    

    def full_name(self):
        return f'{self.parent.name} / {self.name}'



class PowerOutput(PowerBaseElement):


    def __init__(self, *, parent: "PowerComponent", name: "str|None" = None, v_out: float, i_out_max: "float|None" = None, p_out_max: "float|None" = None):
        if name is None:
            name = f'{v_out:.3g} V Out'
        super().__init__(name)
        self.parent = parent
        self.v_out, self.i_out_max, self.p_out_max = v_out, i_out_max, p_out_max
        self._sinks = [] # type: list[PowerInput]
        self.i_out_calc, self.p_out_calc = None, None
    

    def __repr__(self) -> str:
        return f'<PowerOutput({self.full_name()})>'

    
    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        pass


    def add_sink(self, sink: "PowerInput|PowerComponent") -> "PowerComponent|PowerInput":
        if isinstance(sink, PowerInput):
            input = sink
        elif isinstance(sink, PowerComponent):
            input = sink._get_input()
        else:
            raise ValueError()
        input._set_source(self)
        self._sinks.append(input)
        return sink


    def _pre_update(self):
        logging.debug(f'Output({self.full_name()})._pre_update()')
        pass


    def _update(self):
        logging.debug(f'Output({self.full_name()})._update()')
        self.i_out_calc = 0
        for sink in self._sinks:
            self.i_out_calc += sink.i_in
        self.p_out_calc = abs(self.v_out * self.i_out_calc)


    def _check(self, raise_severe_errors: bool) -> bool:
        logging.debug(f'Output({self.full_name()})._check()')
        sinks_ok = True
        self.clear_warnings()
        if self.p_out_max is not None:
            if self.p_out_calc > self.p_out_max:
                self._warn(f'Max. output power exceeded')
        if self.i_out_max is not None:
            if self.i_out_calc > self.i_out_max:
                self._warn(f'Max. output current exceeded')
        return self.ok()
    

    def full_name(self, include_group: bool = False):
        result = f'{self.parent.name} / {self.name}'
        if include_group:
            result += f' ({self.parent.group})'
        return result
