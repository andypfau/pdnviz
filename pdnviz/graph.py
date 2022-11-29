from .power_base import *
from .power_component import PowerComponent
from .systools import get_tempfile_path, ensure_directories
from .formatting import si_prefixed
from graphviz import Digraph



class PowerGraph:


    def __init__(self, root_component: "PowerComponent", grouped: bool = False, dissipation: bool = False, engine: str = None):
        
        if engine is None: engine = 'dot'
        
        self.root, self.groups, self.dissipation, self.engine = root_component, grouped, dissipation, engine

        self._rendered_components = []
        self._component_clusters = {}
        self._pdiss_start_nodes = {}
        self._pdiss_end_nodes = {}
        self._input_nodes = {}
        self._output_nodes = {}
        for i_c,component in enumerate(root_component.get_all_components()):
            self._component_clusters[component] = f'cluster_Component{i_c}'
            self._pdiss_start_nodes[component] = f'node_PDiss{i_c}Start'
            self._pdiss_end_nodes[component] = f'node_PDiss{i_c}End'
            for i_i,input in enumerate(component._inputs):
                self._input_nodes[input] = f'node_Component{i_c}Input{i_i}'
            for i_o,output in enumerate(component._outputs):
                self._output_nodes[output] = f'node_Component{i_c}Output{i_o}'

        self._group_clusters = {}
        for i_g,group in enumerate(root_component.get_all_groups()):
            self._group_clusters[group] = f'cluster_Group{i_g}'
        
        root_component.update()
        self._generate()

    
    def save(self, path: str, makedirs: bool = True, view: bool = False):
        if makedirs:
            ensure_directories(path, is_filename=True)
        self.graph.render(filename=path+'.gv', outfile=path, engine=self.engine, view=view, cleanup=True)
    

    def save_dot(self, path, makedirs: bool = True):
        if makedirs:
            ensure_directories(path, is_filename=True)
        self.graph.render(filename=path+'.gv', engine=self.engine)

    
    def view(self, format: str = 'pdf') -> str:
        path = get_tempfile_path()
        dotfile = path + '.gv'
        outfile = path + '.' + format
        self.graph.render(filename=dotfile, outfile=outfile, engine=self.engine, view=True, cleanup=True)
        return outfile

    
    def _component(self, graph: Digraph, component: PowerComponent):

        if component in self._rendered_components:
            return
        self._rendered_components.append(component)

        def make_comp(parent):
            
            with parent.subgraph(name=self._component_clusters[component]) as component_cluster:
                
                component_cluster.attr(shape='box', style='rounded,bold,filled', fillcolor='LightSteelBlue')
                component_cluster.attr(label=component.name)

                for input in component._inputs:
                    component_cluster.attr('node', shape='box', style='filled', fillcolor='BurlyWood')
                    component_cluster.node(self._input_nodes[input], label=input.name)
                for output in component._outputs:
                    component_cluster.attr('node', shape='box', style='filled', fillcolor='DarkOrange')
                    component_cluster.node(self._output_nodes[output], label=output.name)
        
                if self.dissipation and component.p_diss_calc > 0:
                    
                    component_cluster.attr('node', shape='point')
                    component_cluster.node(self._pdiss_start_nodes[component])
                    
                    graph.attr('node', shape='point')
                    graph.node(self._pdiss_end_nodes[component])
                    
                    graph.attr('edge', label='')
                    graph.attr('edge', headlabel=f'{si_prefixed(component.p_diss_calc,"W")}')
                    graph.edge(self._pdiss_start_nodes[component], self._pdiss_end_nodes[component], ltail=self._component_clusters[component])

        if self.groups:
            with graph.subgraph(name=self._group_clusters[component.group]) as group_cluster:
                group_cluster.attr(shape='box', style='dashed')
                group_cluster.attr(label=component.group)
                make_comp(group_cluster)
        else:
            make_comp(graph)


    def _recurse(self, graph: Digraph, component: PowerComponent):

        self._component(graph, component)

        for output in component._outputs:
            for input in output._sinks:
                subcomponent = input.parent

                self._recurse(graph, subcomponent)
                
                graph.attr('edge', label=f'{si_prefixed(input.i_in,"A")}\n{si_prefixed(input.p_in_calc,"W")}')
                graph.attr('edge', headlabel=si_prefixed(input.v_in_actual,'V'))
                graph.edge(self._output_nodes[output], self._input_nodes[input])
    

    def _generate(self):

        self.graph = Digraph('pdn_graph')
        self.graph.attr('edge', fontsize='8')

        self._recurse(self.graph, self.root)
