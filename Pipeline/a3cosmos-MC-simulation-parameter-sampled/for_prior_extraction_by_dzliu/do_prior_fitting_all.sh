#!/bin/bash
# 


IFS=$'\n' read -d '' -r -a list_of_projects < "list_of_sim_projects.txt"

for (( i=0; i<${#list_of_projects[@]} ; i++)); do
    if [[ x"${list_of_projects[i]}" == x ]]; then continue; fi
    name_of_project=$(basename "${list_of_projects[i]}")
    if [[ ! -d "$name_of_project" ]]; then continue; fi
    cd "$name_of_project/"
    if [[ ! -f "do_prior_fitting.sh.galfit.running" ]] && [[ ! -f "do_prior_fitting.sh.galfit.done" ]]; then
        sed -i -e 's/-steps getpix galfit gaussian final/-steps getpix galfit gaussian -sersic final -clean/g' do_prior_fitting.sh
        chmod +x do_prior_fitting.sh
        
        echo "Counting screen task "$(screen -ls | grep "g[0-9]" | wc -l)
        while       [[    6  -le    $(screen -ls | grep "g[0-9]" | wc -l) ]]; do
        sleep            30
        echo "Counting screen task "$(screen -ls | grep "g[0-9]" | wc -l)
        done
        
        echo "----------------------------------------------------------------------------------------"
        echo "$name_of_project "g$((i+1))
        screen -d -S "g$((i+1))" -m bash -c "touch do_prior_fitting.sh.galfit.running; ./do_prior_fitting.sh; rm do_prior_fitting.sh.galfit.running; touch do_prior_fitting.sh.galfit.done" 
        #break
        sleep 15
    fi
    cd "../"
done



