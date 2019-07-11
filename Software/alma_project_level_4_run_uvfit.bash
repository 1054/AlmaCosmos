#!/bin/bash
# 

#source ~/Softwares/CASA/SETUP.bash
#source ~/Softwares/GILDAS/SETUP.bash
#source ~/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash


# read input Project_code

if [[ $# -eq 0 ]]; then
    echo "Usage: "
    echo "    alma_project_level_4_run_uvfit.bash Project_code"
    echo "Example: "
    echo "    alma_project_level_4_run_uvfit.bash 2013.1.00034.S"
    echo "Notes: "
    echo "    This code will run uv_fit for all uvt files under Level_4_Data_uvt and output catalog into Level_4_Run_uvfit"
    exit
fi

Project_code="$1"

# define logging files and functions
error_log_file=".$(basename ${BASH_SOURCE[0]}).err"
output_log_file=".$(basename ${BASH_SOURCE[0]}).log"
if [[ -f "$error_log_file" ]]; then mv "$error_log_file" "$error_log_file.2"; fi
if [[ -f "$output_log_file" ]]; then mv "$output_log_file" "$output_log_file.2"; fi

echo_output()
{
    echo "$@"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$output_log_file"
}

echo_error()
{
    echo "*************************************************************"
    echo "$@"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$error_log_file"
    echo "["$(date "+%Y%m%dT%H%M%S")"]" "$@" >> "$output_log_file"
    echo "*************************************************************"
}


# begin
echo_output "Began processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"


# check CASA
#if [[ ! -d "$HOME/Softwares/CASA" ]]; then
#    echo_error "Error! \"$HOME/Softwares/CASA\" was not found!" \
#               "Sorry, we need to put all versions of CASA under \"$HOME/Softwares/CASA/Portable/\" directory!"
#    exit 1
#fi
#if [[ ! -f "$HOME/Softwares/CASA/SETUP.bash" ]]; then
#    echo_error "Error! \"$HOME/Softwares/CASA/SETUP.bash\" was not found!" \
#               "Sorry, please ask Daizhong by emailing dzliu@mpia.de!"
#    exit 1
#fi
#casa_setup_script_path="$HOME/Softwares/CASA/SETUP.bash"


# check GILDAS
if [[ $(type mapping 2>/dev/null | wc -l) -eq 0 ]]; then
    # if not executable in the command line, try to find it in "$HOME/Softwares/GILDAS/"
    if [[ -d "$HOME/Softwares/GILDAS" ]] && [[ -f "$HOME/Softwares/GILDAS/SETUP.bash" ]]; then
        source "$HOME/Softwares/GILDAS/SETUP.bash"
    else
        # if not executable in the command line, nor in "$HOME/Softwares/GILDAS/", report error.
        echo_error "Error! \"mapping\" is not executable in the command line! Please check your \$PATH!"
        exit 1
    fi
fi


# check Crab.Toolkit.PdBI
if [[ $(type casa-ms-split 2>/dev/null | wc -l) -eq 0 ]]; then
    # if not executable in the command line, try to find it in "$HOME/Softwares/GILDAS/"
    if [[ -d "$HOME/Cloud/Github/Crab.Toolkit.PdBI" ]] && [[ -f "$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash" ]]; then
        source "$HOME/Cloud/Github/Crab.Toolkit.PdBI/SETUP.bash"
    else
        # if not executable in the command line, nor in "$HOME/Softwares/GILDAS/", report error.
        echo_error "Error! \"casa-ms-split\" is not executable in the command line! Please check your \$PATH!"
        exit 1
    fi
fi


# check meta data table file
if [[ ! -f "meta_data_table.txt" ]]; then
    echo_error "Error! \"meta_data_table.txt\" was not found! Please run previous steps first!"
    exit 255
fi


# check Level_4_Data_uvt folder
if [[ ! -d Level_4_Data_uvt ]]; then 
    echo_error "Error! \"Level_4_Data_uvt\" does not exist! Please run previous steps first!"
    exit 255
fi


# read Level_4_Data_uvt/DataSet_*
list_of_datasets=($(ls -1d Level_4_Data_uvt/DataSet_* | sort -V))


# prepare Level_4_Run_uvfit folder
if [[ ! -d Level_4_Run_uvfit ]]; then 
    echo_output "mkdir Level_4_Run_uvfit"
    mkdir Level_4_Run_uvfit
fi
echo_output "cd Level_4_Run_uvfit"
cd Level_4_Run_uvfit


# loop datasets and run CASA split then GILDAS importuvfits
for (( i = 0; i < ${#list_of_datasets[@]}; i++ )); do
    
    DataSet_dir=$(basename ${list_of_datasets[i]})
    
    # print message
    echo_output "Now sorting out unique sources in \"$DataSet_dir\" and copying *.uvt"
    
    # check Level_4_Data_uvt subdirectories
    list_of_source_names=($(ls -1d ../Level_4_Data_uvt/$DataSet_dir/* ) )
    if [[ ${#list_of_source_names[@]} -eq 0 ]]; then
        echo_error "Error! \"../Level_4_Data_uvt/$DataSet_dir/\" does not contain any subdirectories?! Please run Level_4_Data_uvt first! We will skip this dataset for now."
        continue
    fi
    
    # prepare Level_4_Run_uvfit DataSet_dir
    if [[ ! -d $DataSet_dir ]]; then
        echo_output "mkdir $DataSet_dir"
        mkdir $DataSet_dir
    fi
    echo_output "cd $DataSet_dir"
    cd $DataSet_dir
    
    # loop list_of_source_names and make dir for each source and copy uvt files
    for (( j = 0; j < ${#list_of_source_names[@]}; j++ )); do
        
        # prepare source_name and create source_name directory
        source_name=${list_of_source_names[j]}
        if [[ ! -d "${source_name}" ]]; then
            echo_output "mkdir ${source_name}"
            mkdir "${source_name}"
        fi
        echo_output "cd ${source_name}"
        cd "${source_name}"
        
        # find and loop uvt files
        list_of_uvt_files=($(ls -1 ../../../Level_4_Data_uvt/$DataSet_dir/split_"${source_name}"_spw*_width*_SP.uvt))
        for (( k = 0; k < ${#list_of_uvt_files[@]}; k++ )); do
            
            # prepare uvt file name and output name
            uvt_filepath="${list_of_uvt_files[k]}"
            uvt_filename=$(basename "${list_of_uvt_files[k]}" | perl -p -e 's/\.(uvt|UVT)$//g')
            uvt_outdir=$(basename "$uvt_filename" | sed -e 's/^split_/run_uvfit_/g')
            uvt_outname=$(basename "$uvt_filename" | sed -e 's/^split_/uvfit_/g')
            
            # link uvt file
            echo_output "ln -fsT $uvt_filepath $uvt_filename.uvt"
            ln -fsT "$uvt_filepath" "$uvt_filename.uvt"
            
            # create working directory
            if [[ ! -d "$uvt_outdir" ]]; then
                echo_output "mkdir $uvt_outdir"
                mkdir "$uvt_outdir"
            fi
            echo_output "cd $uvt_outdir"
            cd "$uvt_outdir"
            
            # link uvt file with a simpler file name
            if [[ ! -f "input.uvt" ]] && [[ ! -L "input.uvt" ]]; then
                echo_output "ln -fsT ../$uvt_filename.uvt input.uvt"
                ln -fsT "../$uvt_filename.uvt" "input.uvt"
            fi
            
            # run uvfit
            if [[ ! -f output_point_model_varied_pos ]]; then
                echo_output "pdbi-uvt-go-uvfit -name input.uvt -offset 0 0 -point -variedpos -out output_point_model_varied_pos"
                pdbi-uvt-go-uvfit -name input.uvt -offset 0 0 -point -variedpos -out output_point_model_varied_pos
            fi
            
            # cd back, out of working dir "$uvt_outdir"
            echo_output "cd ../"
            cd ../
        done
        
        # cd back, out of "${source_name}" dir
        echo_output "cd ../"
        cd ../
    done
    
    # cd back
    echo_output "cd ../"
    cd ../
    
    # print message
    if [[ $i -gt 0 ]]; then
        echo ""
        echo ""
    fi
    
done


echo_output "cd ../"
cd ../


# finish
echo_output "Finished processing ALMA project ${Project_code} with $(basename ${BASH_SOURCE[0]})"
echo_output ""
echo_output ""


# 
# common data directory structure:
# Level_1_Raw
# Level_2_Calib
# Level_3_Split
# Level_4_Data_uvfits
# Level_4_Data_uvt
# Level_4_Run_clean
# Level_4_Run_uvfit
# Level_5_Sci
