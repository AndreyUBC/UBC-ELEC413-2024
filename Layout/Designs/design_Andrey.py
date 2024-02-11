from pya import *

 
def design_Andrey(cell, cell_y, inst_wg1, inst_wg2, inst_wg3, waveguide_type):
    
    # load functions
    from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell
    ly = cell.layout()
    library = ly.technology().name

    cell_taper = ly.create_cell('ebeam_taper_350nm_2000nm_te1310', library)

    #####
    # designer circuit:

    # Create a physical text label so we can see under the microscope
    # How do we find out the PCell parameter variables?
    '''
    c = ly.create_cell('TEXT','Basic')
    [p.name for p in c.pcell_declaration().get_parameters() if c.is_pcell_variant]
    c.delete()
    '''
    # returns: ['text', 'font_name', 'layer', 'mag', 'inverse', 'bias', 'cspacing', 'lspacing', 'eff_cw', 'eff_ch', 'eff_lw', 'eff_dr', 'font']
    from SiEPIC.utils import get_technology_by_name
    TECHNOLOGY = get_technology_by_name(library)
    cell_text = ly.create_cell('TEXT', "Basic", {
        'text':cell.name,
        'layer': TECHNOLOGY['M1'],
        'mag': 30,
         })
    if not cell_text:
        raise Exception ('Cannot load text label cell; please check the script carefully.')
    cell.insert(CellInstArray(cell_text.cell_index(), Trans(Trans.R0, 25000,125000)))                

    # load the cells from the PDK
    # choose appropriate parameters
    cell_bragg = ly.create_cell('ebeam_pcell_bragg_grating', library, {
        'number_of_periods':10,
        'grating_period': 0.272,
        'corrugation_width': 0.05,
        'wg_width': 0.35,
        'sinusoidal': False})
    if not cell_bragg:
        raise Exception ('Cannot load Bragg grating cell; please check the script carefully.')

    waveguide_type_mm = 'Multimode Strip TE 1310 nm, w=2000 nm'

    # Lets start with connection
    height = 20000
    width = 200000

    # instantiate y-branch (attached to input waveguide)
    inst_y1 = connect_cell(inst_wg1, 'opt2', cell_y, 'opt2')
    
    # instantiate Bragg grating (attached to y branch)
    inst_bragg1 = connect_cell(inst_y1, 'opt1', cell_bragg, 'opt1')

    # instantiate taper from 350 nm waveguide y-branch to 385 nm Bragg grating
    inst_taper1 = connect_cell(inst_bragg1, 'opt2', cell_taper, 'opt')
    
    inst_taper2 = connect_cell(inst_taper1, 'opt2', cell_taper, 'opt2')
    inst_taper2.transform(Trans(width,0))
    


    # instantiate Bragg grating (attached to y branch)
    inst_bragg1 = connect_cell(inst_taper1, 'opt2', cell_bragg, 'opt1')

    # instantiate Bragg grating (attached to the first Bragg grating)
    inst_bragg2 = connect_cell(inst_bragg1, 'opt2', cell_bragg, 'opt2')
    
    # move the Bragg grating to the right, and up
    inst_bragg2.transform(Trans(250000,200000))

    #####
    # Waveguides for the two outputs:
    # connect_pins_with_waveguide(inst_y1, 'opt3', inst_wg3, 'opt1', waveguide_type=waveguide_type)

    # instantiate taper from 350 nm waveguide y-branch to 385 nm Bragg grating
    inst_taper4 = connect_cell(inst_bragg2, 'opt1', cell_taper, 'opt2')

    connect_pins_with_waveguide(inst_taper4, 'opt', inst_wg2, 'opt1', waveguide_type=waveguide_type)
    
    '''
    make a long waveguide, back and forth, 
    target 0.2 nm FSR assuming ng = 4
    > wavelength=1270e-9; ng=4; fsr=0.2e-9;
    > L = wavelength**2/2/ng/fsr
    > L * 1e6
    > 1000 [microns]
    using "turtle" routing
    https://github.com/SiEPIC/SiEPIC-Tools/wiki/Scripted-Layout#adding-a-waveguide-between-components
    '''
    # connect_pins_with_waveguide(inst_y1, 'opt3', inst_wg3, 'opt1', waveguide_type=waveguide_type)
    
    

    # Good, outer Waveguide
    try:
        connect_pins_with_waveguide(inst_y1, 'opt3', inst_wg3, 'opt1', 
            waveguide_type='Strip TE 1310 nm, w=350 nm (core-clad)', 
            turtle_A = [10,-90,215,-90,350,90] )
    except:    
        connect_pins_with_waveguide(inst_y1, 'opt3', inst_wg3, 'opt1', 
            waveguide_type='Strip TE 1310 nm, w=385 nm (core-clad)', 
            turtle_A = [10,-90,215,-90,350,-90] )

    '''
    # Good, Inner Waveguide
    try:
        connect_pins_with_waveguide(inst_bragg1, 'opt2', inst_bragg2, 'opt2', 
            waveguide_type='Strip TE 1310 nm, w=385 nm (core-clad)', 
            turtle_A = [325,90,20,90,345,-90,20,-90,300,90,20,90,300,-90,20,-90,300,90,20,90,300,-90,20,-90,300,90,20,90,300,-90,20,-90,300,90,20,90,300,-90,20,-90] )
    except:    
        connect_pins_with_waveguide(inst_bragg1, 'opt2', inst_bragg2, 'opt2', 
            waveguide_type='Strip TE 1310 nm, w=350 nm (core-clad)', 
            turtle_A = [325,90,20,90,345,-90,20,-90,300,90,20,90,300,-90,20,-90,300,90,20,90,300,-90,20,-90,300,90,20,90,300,-90,20,-90,300,90,20,90,300,-90,20,-90] )

            
    '''
    return inst_wg1, inst_wg2, inst_wg3
