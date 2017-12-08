#!/bin/bash
#SBATCH --mail-user=dzliu@mpia-hd.mpg.de
#SBATCH --mail-type=FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --time=24:00:00
#SBATCH --mem=4000
#SBATCH --cpus-per-task=1
#SBATCH --output=log_Step_1_TASK_ID_%a_JOB_ID_%A.out

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



# 
# check host and other dependencies
# 
if [[ $(uname -a) != "Linux isaac"* ]] && [[ " $@ " != *" test "* ]]; then
    echo "This code can only be ran on ISAAC machine!"
    exit 1
fi

if [[ ! -d "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong" ]]; then
    echo "mkdir -p $HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong"
    mkdir -p "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong"
fi

cd "$HOME/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong"

source "$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))/Softwares/SETUP.bash"

if [[ $(type pip 2>/dev/null | wc -l) -eq 0 ]]; then module load anaconda; fi



# 
# download alma project list
# 
almacosmos_gdownload.py "list_project_rms_for_v20170604.sort_V.image_file.txt"

cat "list_project_rms_for_v20170604.sort_V.image_file.txt" | grep -v '^#' | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 8 | grep -v '^2011.0.00064.S' > "list_projects.txt"

if [[ ! -f "list_projects.txt" ]]; then
    echo "Error! Failed to get \"list_project_rms_for_v20170604.sort_V.image_file.txt\" from Google Drive and create \"list_projects.txt\"!"
    exit 1
fi




