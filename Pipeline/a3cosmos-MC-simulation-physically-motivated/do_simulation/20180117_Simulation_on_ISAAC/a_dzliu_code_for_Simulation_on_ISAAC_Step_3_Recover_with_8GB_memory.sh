#!/bin/bash
#SBATCH --mail-user=dzliu@mpia-hd.mpg.de
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --time=48:00:00
#SBATCH --mem=8000
#SBATCH --cpus-per-task=30
#SBATCH --output=log_Step_3_TASK_ID_%a_JOB_ID_%A.out

# 
# This script will run galfit on 
# the simulated images in "Simulated/"
# and output "Recovered/"
# 

# 
# to run this script in Slurm job array mode
# sbatch --array=1-120%5 -N1 ~/Cloud/Github/Crab.Toolkit.CAAP/batch/a_dzliu_code_for_ISAAC_Simulation_Step_3_Recover.sh
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



# check host and other dependencies
if [[ $(uname -a) != "Linux isaac"* ]] && [[ " $@ " != *" test "* ]]; then
    echo "This code can only be ran on ISAAC machine!"
    exit 1
fi

if [[ ! -f "$SLURM_SUBMIT_DIR/list_projects.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Work_Dir.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Script_Dir.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Data_Version.txt" ]] || \
    [[ ! -f "$SLURM_SUBMIT_DIR/Input_Galaxy_Modeling_Dir.txt" ]]; then
    echo "Error! Please run \"a_dzliu_code_for_Simulation_on_ISAAC_Step_1_List_Projects.sh\" first!"
    exit 1
fi

Work_Dir=$SLURM_SUBMIT_DIR

Script_Dir=$(cat "$SLURM_SUBMIT_DIR/Input_Script_Dir.txt")

#Data_Version=$(cat "$SLURM_SUBMIT_DIR/Input_Data_Version.txt")

#Input_Galaxy_Modeling_Dir=$(cat "$SLURM_SUBMIT_DIR/Input_Galaxy_Modeling_Dir.txt")

if [[ ! -d "$Work_Dir" ]]; then
    echo "Error! \"$Work_Dir\" was not found! Please create that directory then run this code again!"
    exit 1
fi

if [[ ! -d "$Script_Dir" ]]; then
    echo "Error! \"$Script_Dir\" was not found! Please create that directory then run this code again!"
    exit 1
fi

#if [[ ! -d "$Input_Galaxy_Modeling_Dir" ]]; then
#    echo "Error! \"$Input_Galaxy_Modeling_Dir\" was not found! Please ask liudz1054@gmail.com to copy that directory then run this code again!"
#    exit 1
#fi

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

if [[ ! -f "list_projects.txt" ]]; then
    echo "Error! \"list_projects.txt\" was not found under current directory! Please run \"a_dzliu_code_for_Simulation_on_ISAAC_Step_1_List_Projects.sh\" first!"
    exit 1
fi

if [[ ! -d "Input_images" ]]; then
    echo "Error! Input_images was not found! Please run \"a_dzliu_code_for_Simulation_on_ISAAC_Step_2_Simulate.sh\" first!"
    exit 1
fi



# 
# prepare physical parameter grid
# 
Input_z=("1.000" "2.000" "3.000" "4.000" "5.000" "6.000")
Input_lgMstar=("09.00" "09.50" "10.00" "10.50" "11.00" "11.50" "12.00")
Input_Type_SED=("MS" "SB")
IFS=$'\n' read -d '' -r -a FitsNames < "list_projects.txt"

if [[ " $@ " == *" test "* ]]; then
Input_z=("5.000")
Input_lgMstar=("11.00")
Input_Type_SED=("MS")
FitsNames=( \
    "2015.1.00379.S_SB1_GB1_MB1_VUDS5170072382_sci.spw0_1_2_3" \
)
fi



#echo "FitsNames = ${FitsNames[@]}"

for (( i=0; i<${#FitsNames[@]}; i++ )); do
    
    # check FitsName not empty
    if [[ x"${FitsNames[i]}" == x"" ]]; then
        continue
    fi
    
    # get FitsName without path and suffix
    FitsName=$(basename "${FitsNames[i]}" | sed -e 's/\.cont.I.image.fits//g')
    
    # check parallel
    if [[ x"$SLURM_ARRAY_TASK_ID" != x"" ]]; then
        if [[ $SLURM_ARRAY_TASK_ID -ne $((i+1)) ]]; then
            continue
        fi
    fi
    
    # check previous output
    if [[ -f "Recovered/$FitsName/done" ]]; then
        echo "Found \"Recovered/$FitsName/done\"! Skip and continue!"
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
    if [[ ! -f "Input_images/$FitsName.cont.I.image.fits" ]]; then
        echo "\"Input_images/$FitsName.cont.I.image.fits\" was not found!"
        exit 1
    else
        echo "Checking \"Input_images/$FitsName.cont.I.image.fits\""
    fi
    
    # get wavelength from fits header
    obsfreq=$(gethead "Input_images/$FitsName.cont.I.image.fits" CRVAL3)
    obswave=$(awk "BEGIN {print 2.99792458e5/($obsfreq/1e9);}")
    if [[ "$obswave"x == ""x ]]; then
        echo "Error! Failed to get observation frequency/wavelength from the fits header keyword CRVAL3 of input fits file \"Input_images/$FitsName.cont.I.image.fits\"!"
        exit 1
    fi
    
    # check simulated directory
    if [[ ! -d "Simulated/$FitsName" ]]; then
        echo "\"Simulated/$FitsName\" was not found!"
        exit 1
    fi
    
    # make recovered directory
    if [[ ! -d "Recovered/$FitsName" ]]; then
        mkdir -p "Recovered/$FitsName"
    fi
    
    # cd recovered directory
    cd "Recovered/$FitsName/"
    
    # backup final data table
    #if [[ -f "datatable_Recovered_getpix.txt" ]]; then
    #    if [[ -f "datatable_Recovered_getpix.txt.backup" ]]; then
    #        mv "datatable_Recovered_getpix.txt.backup" "datatable_Recovered_getpix.txt.backup.backup"
    #    fi
    #    mv "datatable_Recovered_getpix.txt" "datatable_Recovered_getpix.txt.backup"
    #fi
    #if [[ -f "datatable_Recovered_galfit.txt" ]]; then
    #    if [[ -f "datatable_Recovered_galfit.txt.backup" ]]; then
    #        mv "datatable_Recovered_galfit.txt.backup" "datatable_Recovered_galfit.txt.backup.backup"
    #    fi
    #    mv "datatable_Recovered_galfit.txt" "datatable_Recovered_galfit.txt.backup"
    #fi
    
    # loop
    for i_w in "${obswave}"; do
        for i_z in "${Input_z[@]}"; do
            for i_lgMstar in "${Input_lgMstar[@]}"; do
                for i_Type_SED in "${Input_Type_SED[@]}"; do
                    
                    # Check output directory, delete failed runs
                    do_Photometry=0
                    if [[ -d "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]]; then
                        if [[ ! -f "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/List_of_Input_Sci_Images.txt" ]]; then
                            echo ""
                            echo "rm -rf \"w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\""
                            echo ""
                            rm -rf "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}"
                            echo ""
                            echo "rm -rf \"Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\" 2>/dev/null"
                            echo ""
                            rm -rf "Read_Results_of_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" 2>/dev/null
                            sleep 5
                                    do_Photometry=1
                        else
                            IFS=$'\n' read -d '' -r -a List_images < "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/List_of_Input_Sci_Images.txt"
                            for (( i3=0; i3<${#List_images[@]}; i3++ )); do
                                Image_name=$(basename "${List_images[i3]}" | sed -e 's/.fits$//g')
                                if [[ ! -d "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/astrodepth_prior_extraction_photometry/${Image_name}" ]]; then
                                    # if a sub sim image dir does not exist, then do it. 
                                    do_Photometry=1
                                    break
                                elif [[ $(find "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/astrodepth_prior_extraction_photometry/${Image_name}" -name "*lock*" | wc -l) -gt 0 ]]; then
                                    # if there are any locked processes (which are probably unfinished!), redo the photometry for this sub sim image. 
                                    echo ""
                                    echo "rm -rf \"w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/astrodepth_prior_extraction_photometry/${Image_name}/\"*"
                                    echo ""
                                    rm -rf "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/astrodepth_prior_extraction_photometry/${Image_name}/"*
                                    sleep 5
                                    do_Photometry=1
                                    break
                                fi
                            done
                        fi
                    fi
                    
                    # Run a3cosmos-prior-extraction-photometry
                    if [[ ! -d "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]] || [[ $do_Photometry -eq 1 ]]; then
                        # 
                        echo "a3cosmos-prior-extraction-photometry \\"
                        echo "    -out \"w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\" \\"
                        echo "    >> \"log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log\""
                        # 
                        echo ""                                              >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        echo ""                                              >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        echo ""                                              >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        echo "Current Time: "$(date +"%Y-%m-%d %H:%M:%S %Z") >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        echo ""                                              >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        echo ""                                              >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        echo ""                                              >> "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log"
                        # 
                        if [[ ! -d "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" ]]; then
                            a3cosmos-prior-extraction-photometry \
                                -cat "../../Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/galaxy_model_id_ra_dec.txt" \
                                -sci "../../Simulated/$FitsName/w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}/image_sim.fits" \
                                -out                           "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" \
                                -unlock getpix galfit gaussian sersic final \
                                >>                         "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log" \
                                &
                        else
                            a3cosmos-prior-extraction-photometry \
                                -out                           "w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}" \
                                -unlock getpix galfit gaussian sersic final \
                                >>                         "log_w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}.log" \
                                &
                        fi
                        sleep 10
                        #ps aux | grep "a3cosmos-prior-extraction-photometry"
                        #ps aux | grep "a3cosmos-prior-extraction-photometry" | grep -v "grep"
                        #ps aux | grep "a3cosmos-prior-extraction-photometry" | grep -v "grep" | wc -l
                        check_simultaneous_processes=$(ps aux | grep "a3cosmos-prior-extraction-photometry" | grep -v "grep" | wc -l)
                        echo "Checking current simultaneous processes of a3cosmos-prior-extraction-photometry $FitsName ($check_simultaneous_processes)"
                        limit_simultaneous_processes=15 # 20171106 20
                        while [[ $check_simultaneous_processes -ge $limit_simultaneous_processes ]]; do
                            sleep 30
                            check_simultaneous_processes=$(ps aux | grep "a3cosmos-prior-extraction-photometry" | grep -v "grep" | wc -l)
                            echo "Checking current simultaneous processes of a3cosmos-prior-extraction-photometry $FitsName ($check_simultaneous_processes)"
                        done
                    else
                        echo "Seems no need to re-run the photometry for \"w_${i_w}_z_${i_z}_lgMstar_${i_lgMstar}_${i_Type_SED}\"."
                    fi
                done
            done
        done
    done
    
    # wait
    wait
    
    # cd back
    cd "../../"
    
    # Done
    date +"%Y-%m-%d %H:%M:%S %Z" > "Recovered/$FitsName/done"
    
    #<TODO><DBEUG># 
    #break
    
done





