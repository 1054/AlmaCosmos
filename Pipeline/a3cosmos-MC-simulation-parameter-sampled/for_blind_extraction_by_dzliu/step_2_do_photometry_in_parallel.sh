#!/bin/bash
# 

#set -e



if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry, this code can only be ran on aida42198 machine!"
    exit 255
fi


if [[ $(dirname $(pwd)) != "statistics_GALFIT" ]]; then
    echo "Error! Current directory name is not \"statistics_GALFIT\"!"
    exit 255
fi


if [[ ! -f "list_of_sim_projects.txt" ]]; then
    echo "Error! \"\" does not exist! Please run task_1_*.sh first!"
    exit 255
fi





echo ""
echo "This code will produce a list of commands into a \"list_of_commands.txt\" file, "
echo "then execute the commands with the tool \"almacosmos_cmd_run_in_parallel\". "
echo ""
echo "Sleeping for 5 seconds then start ..."
sleep 5
echo ""


IFS=$'\n' read -d '' -r -a list_of_sim_projects < "list_of_sim_projects.txt"
for (( i = 0; i < ${#list_of_sim_projects[@]}; i++ )); do
    if [[ x"${list_of_sim_projects[i]}" == x ]]; then
        continue
    fi
    sim_project="${list_of_sim_projects[i]}"
    sim_project_name=$(basename "${list_of_sim_projects[i]}")
    # 
    # check if this sim project has already been prepared well
    if [[ ! -f "$sim_project_name/do_prior_fitting.sh.ok" ]]; then
        echo "Error! \"$sim_project_name/do_prior_fitting.sh.ok\" was not found! Please run task_1_*.sh first!"
        exit 255
    fi
    # 
    echo "cd \"$(pwd)/$sim_project_name\"; ./do_prior_fitting.sh; cd ../" >> "list_of_commands_for_prior_fitting.txt"
done


echo ""
echo "Then, please run"
echo "  almacosmos_cmd_run_in_parallel \"list_of_commands_for_prior_fitting.txt\""
echo ""





