#!/bin/bash
#SBATCH --mail-user=dzliu@mpia-hd.mpg.de
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --time=24:00:00
#SBATCH --mem=4000
#SBATCH --cpus-per-task=2
#SBATCH --output=log_Step_2_TASK_ID_%a_JOB_ID_%A.out

# 
# This script will load galaxy modeling results from "$HOME/Work/AlmaCosmos/Simulation/Cosmological_Galaxy_Modelling_for_COSMOS"
# and read ALMA images from "Google Drive"
# and read source-removed ALMA residual images from "Google Drive"
# and output simulated images to "Simulated/"
# 

# 
# to run this script in Slurm job array mode
# sbatch --array=1-1%1 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_2_Simulate.sh test
# sbatch --array=1-1%1 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_2_Simulate.sh
# sbatch --array=1-136%1 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_2_Simulate.sh
# 

echo "Hostname: "$(/bin/hostname)
echo "PWD: "$(/bin/pwd)
echo "SLURM_JOBID: "$SLURM_JOBID
echo "SLURM_JOB_NODELIST: "$SLURM_JOB_NODELIST
echo "SLURM_NNODES: "$SLURM_NNODES
echo "SLURM_ARRAY_TASK_ID: "$SLURM_ARRAY_TASK_ID
echo "SLURM_ARRAY_JOB_ID: "$SLURM_ARRAY_JOB_ID
echo "SLURMTMPDIR: "$SLURMTMPDIR
echo "SLURM_SUBMIT_DIR: "$SLURM_SUBMIT_DIR



# 
# check host and other dependencies
# 
if [[ $(hostname) != "isaac"* ]] && [[ $(hostname) != "aida"* ]] && [[ " $@ " != *" test "* ]]; then
    echo "This code can only be ran on ISAAC or AIDA machine!"
    exit 1
fi

if [[ x"$SLURM_SUBMIT_DIR" == x"" ]]; then
    SLURM_SUBMIT_DIR="."
fi

if [[ ! -f "$SLURM_SUBMIT_DIR/list_of_projects.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Work_Dir.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Script_Dir.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Data_Version.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Galaxy_Modeling_Dir.txt" ]]; then
    echo "Error! Please run \"a_dzliu_code_for_Simulation_on_ISAAC_Step_1_Prepare.sh\" and prepare the \"Input*.txt\" and \"list_of_projects.txt\" files first!"
    exit 1
fi

Work_Dir="$SLURM_SUBMIT_DIR"

Script_Dir=$(cat "$SLURM_SUBMIT_DIR/Input_Script_Dir.txt" | grep -v "^#" | head -n 1)

Phot_Version=$(cat "$SLURM_SUBMIT_DIR/Input_Phot_Version.txt" | grep -v "^#" | head -n 1)

Data_Version=$(cat "$SLURM_SUBMIT_DIR/Input_Data_Version.txt" | grep -v "^#" | head -n 1)

Input_Galaxy_Modeling_Dir=$(cat "$SLURM_SUBMIT_DIR/Input_Galaxy_Modeling_Dir.txt")

if [[ ! -d "$Work_Dir" ]]; then
    echo "Error! \"$Work_Dir\" was not found! Please create that directory then run this code again!"
    exit 1
fi

if [[ ! -d "$Script_Dir" ]]; then
    echo "Error! \"$Script_Dir\" was not found! Please create that directory then run this code again!"
    exit 1
fi

if [[ ! -d "$Input_Galaxy_Modeling_Dir" ]]; then
    echo "Error! \"$Input_Galaxy_Modeling_Dir\" was not found! Please ask liudz1054@gmail.com to copy that directory then run this code again!"
    exit 1
fi

source "$Script_Dir/Softwares/SETUP.bash"

source "$Script_Dir/Pipeline/SETUP.bash"

pwd

cd "$Work_Dir"

if [[ $(type pip 2>/dev/null | wc -l) -eq 0 ]]; then
    module load anaconda
fi

if [[ $(type sm 2>/dev/null | wc -l) -eq 0 ]]; then 
    echo "Error! Supermongo was not installed!"
    exit
fi

if [[ $(echo "load astroSfig.sm" | sm 2>&1 | wc -l) -ne 0 ]]; then 
    echo "Error! Supermongo does not contain necessary macros! Please contact liudz1054@gmail.com!"
    exit
fi



# 
# prepare physical parameter grid
# 
Input_z=($(seq 1.0 0.25 6.0 | awk '{printf "%0.3f\n",$1}')) # N=21
Input_lgMstar=($(seq 9.0 0.25 12.0 | awk '{printf "%0.3f\n",$1}')) # N=13
Input_Type_SED=("MS" "SB") # N=2
IFS=$'\n' read -d '' -r -a FitsNames < "list_of_projects.txt"

if [[ " $@ " == *" test "* ]]; then
    Input_z=("1.000")
    Input_lgMstar=("11.00")
    Input_Type_SED=("MS")
    FitsNames=("2012.1.00523.S_SB1_GB1_MB1_hz3_sci.spw0_1_2_3")
fi



#echo "FitsNames = ${FitsNames[@]}"

if [[ ! -d "Input_images" ]]; then
    mkdir "Input_images"
fi

for (( i=0; i<${#FitsNames[@]}; i++ )); do
    
    # check FitsName not empty
    if [[ x"${FitsNames[i]}" == x"" ]]; then
        continue
    fi
    
    # get FitsName without path and suffix
    FitsName=$(basename "${FitsNames[i]}" | sed -e 's/\.cont.I.image.fits//g')
    
    # check parallel
    if [[ ! -z $SLURM_ARRAY_TASK_ID ]]; then
        if [[ $SLURM_ARRAY_TASK_ID -ne $((i+1)) ]]; then
            continue
        fi
    fi
    
    # check previous output
    if [[ -f "Simulated/$FitsName/done" ]]; then
        echo "Found \"Simulated/$FitsName/done\"! Skip and continue!"
        continue
    fi
    
    # check non-COSMOS fields
    if [[ "$FitsName" == "2011.0.00539.S_"*"_ECDFS02_"* ]] || \
        [[ "$FitsName" == "2011.0.00539.S_"*"_ELS01_"* ]] || \
        [[ "$FitsName" == "2011.0.00539.S_"*"_ADFS01_"* ]] || \
        [[ "$FitsName" == "2011.0.00539.S_"*"_XMM01_"* ]] || \
        [[ "$FitsName" == "2011.0.00742.S_"*"__RX_J094144.51+385434.8__"* ]] || \
        [[ "$FitsName" == "2012.1.00596.S_"*"_PKS0215+015_"* ]] ; then
        echo "Warning! \"$FitsName\" is a non-COSMOS field! Skip and continue!"
        continue
    fi
    
    # check very high-res. images
    if [[ "$FitsName" == *"2015.1.00607.S_SB1_GB1_MB1_AzTEC-3_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB1_GB1_MB1_COSMOS_824759_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB2_GB1_MB1_COSMOS_823380_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB3_GB1_MB1_COSMOS_822872_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB3_GB1_MB1_COSMOS_822965_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB4_GB1_MB1_COSMOS_810344_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00695.S_SB4_GB1_MB1_COSMOS_839268_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.00928.S_SB3_GB1_MB1_LBG-1_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.01345.S_SB1_GB1_MB1_AzTEC1_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.01345.S_SB1_GB1_MB1_AzTEC4_sci.spw0_1_2_3"* ]] || \
        [[ "$FitsName" == *"2015.1.01345.S_SB2_GB1_MB1_AzTEC8_sci.spw0_1_2_3"* ]] ; then
        echo "Warning! \"$FitsName\" is a very high-res. image! Skip and continue!"
        continue
    fi
    
    # check input image
    # -- previous: "Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/20170930/Output_Residual_Images/$FitsName.cont.I.residual.fits"
    for file_to_download in \
        "Photometry/ALMA_full_archive/Blind_Extraction_by_Benjamin/$Phot_Version/Output_Residual_Images/$FitsName.cont.I.residual.fits" \
        "Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/$Data_Version/fits_cont_I_image/$FitsName.cont.I.image.fits" \
        "Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/$Data_Version/fits_cont_I_image_pixel_histograms/$FitsName.cont.I.image.fits.pixel.statistics.txt" \
        "Data/ALMA_full_archive/Calibrated_Images_by_Benjamin/$Data_Version/fits_cont_I_clean-beam/$FitsName.cont.I.clean-beam.fits"
        do
        if [[ ! -f "Input_images/$(basename $file_to_download)" ]] && [[ ! -L "Input_images/$(basename $file_to_download)" ]]; then
            cd "Input_images/"
            almacosmos_gdownload.py "$file_to_download" #<TODO># now we do not download from Google, but directly rsync to there.
            cd "../"
        fi
        if [[ ! -f "Input_images/$(basename $file_to_download)" ]] && [[ ! -L "Input_images/$(basename $file_to_download)" ]]; then
            echo "Error! Failed to get the image file \"$file_to_download\" from Google Drive! Please re-try!"
            exit 1
        fi
    done
    
    # check BUNIT in fits header
    fits_header_BUNIT=$(gethead "Input_images/$FitsName.cont.I.residual.fits" BUNIT)
    if [[ "$fits_header_BUNIT"x == ""x ]]; then
        echo "Warning! No BUNIT in the fits header of the input fits file \"Input_images/$FitsName.cont.I.image.fits\"!"
        echo "Adding BUNIT=\"Jy/beam\""
        sethead "Input_images/$FitsName.cont.I.residual.fits" BUNIT="Jy/beam"
    fi
    
    # get wavelength from fits header
    obsfreq=$(gethead "Input_images/$FitsName.cont.I.image.fits" CRVAL3)
    obswave=$(awk "BEGIN {print 2.99792458e5/($obsfreq/1e9);}")
    if [[ "$obswave"x == ""x ]]; then
        echo "Error! Failed to get observation frequency/wavelength from the fits header keyword CRVAL3 of input fits file \"Input_images/$FitsName.cont.I.image.fits\"!"
        exit 1
    fi
    
    # get rms noise
    rmsnoise=$(cat "Input_images/$FitsName.cont.I.image.fits.pixel.statistics.txt" | grep "Gaussian_sigma" | perl -p -e 's/.+ = ([^#]+)/\1/g')
    if [[ "$rmsnoise"x == ""x ]]; then
        echo "Error! Failed to get rms noise from \"Input_images/$FitsName.cont.I.image.fits.pixel.statistics.txt\"!"
        exit 1
    fi
    
    # backup simulated data table
    if [[ -f "Simulated/$FitsName/datatable_Simulated.txt" ]]; then
        if [[ -f "Simulated/$FitsName/datatable_Simulated.txt.backup" ]]; then
            mv "Simulated/$FitsName/datatable_Simulated.txt.backup" "Simulated/$FitsName/datatable_Simulated.txt.backup.backup"
        fi
        mv "Simulated/$FitsName/datatable_Simulated.txt" "Simulated/$FitsName/datatable_Simulated.txt.backup"
    fi
    
    # loop
    for i_w in "${obswave}"; do
        for i_z in "${Input_z[@]}"; do
            for i_lgMstar in "${Input_lgMstar[@]}"; do
                for i_Type_SED in "${Input_Type_SED[@]}"; do
                    
                    if [[ ! -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" ]]; then
                        
                        echo "almacosmos_simulate_image_based_on_galaxy_modeling \\"
                        echo "    -w \"$i_w\" -z \"${i_z}\" -lgMstar \"${i_lgMstar}\" -Type-SED \"${i_Type_SED}\""
                        
                        almacosmos_simulate_image_based_on_galaxy_modeling \
                            -sci "Input_images/$FitsName.cont.I.image.fits" \
                            -psf "Input_images/$FitsName.cont.I.clean-beam.fits" \
                            -res "Input_images/$FitsName.cont.I.residual.fits" \
                            -gal "$Input_Galaxy_Modeling_Dir" \
                            -w "$i_w" -z "${i_z}" -lgMstar "${i_lgMstar}" -Type-SED "${i_Type_SED}" \
                            -rms-noise $rmsnoise -snr-peak-threshold 3.0 \
                            -out "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                        
                        if [[ ! -d "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName" ]]; then
                            echo "Error! Failed to run \"almacosmos_simulate_image_based_on_galaxy_modeling\" and create \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\" directory!"
                            exit 1
                        fi
                        
                        cd "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName/"
                        cp galaxy_model_*.txt ../
                        if [[ -f "image_sim.fits" ]]; then cp "image_sim.fits" ../; elif [[ -f "too_faint" ]]; then cp "too_faint" ../; fi
                        cd "../../../../"
                        
                        if [[ ! -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" ]] && \
                            [[ ! -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/too_faint" ]]; then
                            echo "Error! Failed to run \"almacosmos_simulate_image_based_on_galaxy_modeling\" and create \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits\" file!"
                            exit 1
                        fi
                        
                        # clean
                        if [[ " $@ " != *" test "* ]]; then
                            rm -rf "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName."*
                            rm -rf "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/$FitsName"
                        fi
                        
                    else
                        
                        echo "Found existing \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits\", skip and continue!"
                        
                    fi
                    
                    
                    # Concat simulated datatable
                    if [[ -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt" ]]; then
                        
                        if [[ $(uname) == Darwin ]]; then
                            xargs_command="gxargs"
                        else
                            xargs_command="xargs"
                        fi
                        
                        if [[ ! -f "Simulated/$FitsName/datatable_Simulated.txt" ]]; then
                            head -n 1 "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt" | $xargs_command -d '\n' -I {} printf "%s  %15s   %s\n" {} "wavelength_um" "sim_dir_str" \
                                    > "Simulated/$FitsName/datatable_Simulated.txt"
                        fi
                        cat "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt" | tail -n +3 | $xargs_command -d '\n' -I {} printf "%s  %15.6f   %s\n" {} "$i_w" "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" \
                                    >> "Simulated/$FitsName/datatable_Simulated.txt"
                        
                        echo "Reading \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt\""
                        
                    elif [[ ! -f "Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/too_faint" ]]; then
                        
                        echo "Warning! \"Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec_flux.txt\" was not found! ******"
                        
                    fi
                    
                done
            done
        done
    done
    
    # Done
    date +"%Y-%m-%d %H:%M:%S %Z" > "Simulated/$FitsName/done"
    
    #<TODO><DBEUG># 
    #break
    
done

