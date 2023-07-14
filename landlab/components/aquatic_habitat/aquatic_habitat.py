"""Landlab component that simulates detachment-limited river erosion.

This component calculates changes in elevation in response to
vertical incision.
"""

import numpy as np
from scipy.interpolate import interp1d

from landlab import Component

class AquaticHabitat(Component):
    """Simulate detachment limited sediment transport.

    Landlab component that simulates detachment limited sediment transport is more
    general than the stream power component. Doesn't require the upstream node
    order, links to flow receiver and flow receiver fields. Instead, takes in
    the discharge values on NODES calculated by the OverlandFlow class and
    erodes the landscape in response to the output discharge.

    As of right now, this component relies on the OverlandFlow component
    for stability. There are no stability criteria implemented in this class.
    To ensure model stability, use StreamPowerEroder or FastscapeEroder
    components instead.

    .. codeauthor:: Nicole Hucke and Angel Monsalve

    Examples
    --------
    >>> import numpy as np
    >>> from landlab import RasterModelGrid
    >>> from landlab.components import AquaticHabitat

    Create a grid on which to calculate detachment ltd sediment transport.

    >>> grid = RasterModelGrid((4, 5))

    The grid will need some data to provide the detachment limited sediment
    transport component. To check the names of the fields that provide input to
    the detachment ltd transport component, use the *input_var_names* class
    property.

    Create fields of data for each of these input variables.

    Using the set topography, now we will calculate slopes on all nodes.

    Now we will arbitrarily add water depth to each node for simplicity.
    >>> grid.at_node['surface_water__depth'] = np.full(grid.number_of_nodes,12.87)
    
        Now we will arbitrarily add water velocity to each node for simplicity.
    >>> grid.at_node['surface_water__velocity'] = np.full(grid.number_of_nodes,2.57)

    Instantiate the `AquaticHabitat` component to work on this grid, and
    run it. In this simple case, we need to pass it a time step ('dt')

    >>> dt = 10.0
    >>> aqhab = AquaticHabitat(grid)
    >>> aqhab.run_one_step(dt=dt)

    After calculating the erosion rate, the elevation field is updated in the
    grid. Use the *output_var_names* property to see the names of the fields that
    have been changed.

    >>> aqhab.output_var_names
    ('topographic__elevation',)

    The `topographic__elevation` field is defined at nodes.

    >>> aqhab.var_loc('topographic__elevation')
    'node'


    Now we test to see how the topography changed as a function of the erosion
    rate.

    >>> grid.at_node['topographic__elevation'] # doctest: +NORMALIZE_WHITESPACE
    array([ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
            0.99936754,  0.99910557,  0.99910557,  0.99910557,  0.99936754,
            1.99955279,  1.99936754,  1.99936754,  1.99936754,  1.99955279,
            2.99968377,  2.99955279,  2.99955279,  2.99955279,  2.99968377])

    References
    ----------
    **Required Software Citation(s) Specific to this Component**

    None Listed

    **Additional References**

    Howard, A. (1994). A detachment-limited model of drainage basin evolution. Water
    Resources Research  30(7), 2261-2285. https://dx.doi.org/10.1029/94wr00757
    """

    _name = "AquaticHabitat"

    _unit_agnostic = True

    _info = {
        "surface_water__depth": {
            "dtype": float,
            "intent": "in",
            "optional": False,
            "units": "m",
            "mapping": "node",
            "doc": "Depth of water on the surface",
        },
        "surface_water__velocity": {
            "dtype": float,
            "intent": "in",
            "optional": False,
            "units": "m/s",
            "mapping": "node",
            "doc": "Average velocity of the surface water",
        },
        "bed_surface__median_grain_size": {
            "dtype": float,
            "intent": "in",
            "optional": True,
            "units": "mm",
            "mapping": "node",
            "doc": "Bed surface median grain size",
        },
    }

    def __init__(
        self,
        grid,
        species='salmon',
        method='HSI',
        D50="bed_surface__median_grain_size",
    ):
        """Calculate detachment limited erosion rate on nodes.

        Landlab component that generalizes the detachment limited erosion
        equation, primarily to be coupled to the the Landlab OverlandFlow
        component.

        This component adjusts topographic elevation.

        Parameters
        ----------
        grid : RasterModelGrid
            A landlab grid.
        K_sp : float, optional
            K in the stream power equation (units vary with other parameters -
            if used with the de Almeida equation it is paramount to make sure
            the time component is set to *seconds*, not *years*!)
        m_sp : float, optional
            Stream power exponent, power on discharge
        n_sp : float, optional
            Stream power exponent, power on slope
        uplift_rate : float, optional
            changes in topographic elevation due to tectonic uplift
        entrainment_threshold : float, optional
            threshold for sediment movement
        slope : str
            Field name of an at-node field that contains the slope.
        """
        super().__init__(grid)

        #assert slope in grid.at_node 

        self._species = species
        self._method = method

        self._I = self._grid.zeros(at="node")  # noqa: E741
        self._dzdt = self._grid.zeros(at="node")

    def run_one_step(self, dt):
        """Erode into grid topography.

        For one time step, this erodes into the grid topography using
        the water discharge and topographic slope.

        The grid field 'topographic__elevation' is altered each time step.

        Parameters
        ----------
        dt : float
            Time step.
        """
        species = self._species
        HSI = self.find_depth_HSI(species)
        
        if self._method == 'CSI':
            self.find_CSI(HSI)
        
        
    def find_velocity_HSI(self, species):
        
        h = self._grid.at_node["surface_water__depth"]
        v = self._grid.at_node["surface_water__velocity"]
        
        if species == 'salmon':
        
            hsi = v*h
            print(hsi)
            
        else:
            print('species not found')
            
    def find_depth_HSI(self, species):
        
        if species == 'salmon':
        
            curve_depth = [0, 6.6, 13.1, 1000]
            curve_HSI = [0, 0, 1, 1]
            
            # Interpolation function
            interpolation_function = interp1d(curve_depth, curve_HSI, kind='linear')
            
            # Interpolate HSI values at the given depth values
            depth_HSI = interpolation_function(self._grid.at_node["surface_water__depth"])
            
            print('The HSI for depth is:')
            print(depth_HSI)
            
    def find_CSI(self,HSI):
        print('you have chosen CSI method')

