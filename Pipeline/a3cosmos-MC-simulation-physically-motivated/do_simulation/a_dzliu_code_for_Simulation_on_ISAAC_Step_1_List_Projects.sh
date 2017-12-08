#!/bin/bash
#SBATCH --mail-user=dzliu@mpia-hd.mpg.de
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --time=24:00:00
#SBATCH --mem=4000
#SBATCH --cpus-per-task=1
#SBATCH --output=log_Step_1_TASK_ID_%a_JOB_ID_%A.out

# 
# This script will download list_of_project.txt
# from "Google Drive"
# 

# 
# to run this script in Slurm job array mode
# sbatch --array=1-1%1 -N1 ~/Cloud/Github/Crab.Toolkit.CAAP/batch/a_dzliu_code_for_ISAAC_Simulation_Step_1_List_Projects.sh
# 
echo "Hostname: "$(/bin/hostname)
echo "PWD: "$(/bin/pwd -P)
echo "SLURM_JOBID: "$SLURM_JOBID
echo "SLURM_JOB_NODELIST: "$SLURM_JOB_NODELIST
echo "SLURM_NNODES: "$SLURM_NNODES
echo "SLURM_ARRAY_TASK_ID: "$SLURM_ARRAY_TASK_ID
echo "SLURM_ARRAY_JOB_ID: "$SLURM_ARRAY_JOB_ID
echo "SLURMTMPDIR: "$SLURMTMPDIR
echo "SLURM_SUBMIT_DIR: "$SLURM_SUBMIT_DIR

Work_Dir="$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong_2"



# 
# check host and other dependencies
# 
if [[ $(uname -a) != "Linux isaac"* ]] && [[ " $@ " != *" test "* ]]; then
    echo "This code can only be ran on ISAAC machine!"
    exit 1
fi

if [[ ! -d "$Work_Dir" ]]; then
    echo "mkdir -p $Work_Dir"
    mkdir -p "$Work_Dir"
fi

if [[ ! -f "$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Softwares/SETUP.bash" ]]; then
    echo "Error! \"$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Softwares/SETUP.bash\" was not found!"
    exit 1
fi

source "$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Softwares/SETUP.bash"

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
# download alma project list
# 
almacosmos_gdownload.py "list_project_rms_for_v20170604.sort_V.image_file.txt"

cat "list_project_rms_for_v20170604.sort_V.image_file.txt" | grep -v '^#' | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 8 | grep -v '^2011.0.00064.S' > "list_projects.txt"

if [[ ! -f "list_projects.txt" ]]; then
    echo "Error! Failed to get \"list_project_rms_for_v20170604.sort_V.image_file.txt\" from Google Drive and create \"list_projects.txt\"!"
    exit 1
fi





