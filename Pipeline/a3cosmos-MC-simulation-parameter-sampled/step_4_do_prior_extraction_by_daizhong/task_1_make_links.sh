#!/bin/bash
# 

#set -e



if [[ $(hostname) != "aida42198" ]]; then
    echo "Sorry, this code can only be ran on aida42198 machine!"
    exit
fi



if [[ ! -d "/disk1/ALMA_COSMOS/A3COSMOS/simulations/output_GALFIT_dzliu" ]]; then
    mkdir -p "/disk1/ALMA_COSMOS/A3COSMOS/simulations/output_GALFIT_dzliu"
    chmod -R 777 "/disk1/ALMA_COSMOS/A3COSMOS/simulations/output_GALFIT_dzliu"
fi
cd "/disk1/ALMA_COSMOS/A3COSMOS/simulations/output_GALFIT_dzliu"



if [[ ! -d "../models" ]]; then
    echo "Error! \"../models\" does not exist!"
    exit 255
fi



if [[ ! -f "list_of_sim_projects.txt" ]]; then
    find "../models" -maxdepth 1 -mindepth 1 -type d > "list_of_sim_projects.txt"
fi
IFS=$'\n' read -d '' -r -a list_of_sim_projects < "list_of_sim_projects.txt"



export IDL_PATH="+$HOME/Softwares/IDL/lib:$IDL_PATH"
#echo "IDL_PATH = $IDL_PATH"



for (( i = 0; i < ${#list_of_sim_projects[@]}; i++ )); do
    
    if [[ x"${list_of_sim_projects[i]}" == x ]]; then
        continue
    fi
    
    sim_project="${list_of_sim_projects[i]}"
    sim_project_name=$(basename "${list_of_sim_projects[i]}")
    
    # 
    # check if this sim project has already been prepared well
    if [[ -f "$sim_project_name/do_prior_fitting.sh.ok" ]]; then
        echo "Found \"$sim_project_name/do_prior_fitting.sh.ok\"! Skip!"
        continue
    fi
    
    # 
    # read _imlist.txt
    sim_imlist_file=$(echo "$sim_project" | sed -e 's/$/_imlist.txt/g')
    if [[ ! -f "$sim_imlist_file" ]]; then
        echo "Error! \"$sim_imlist_file\" does not exist! Skip!"
        echo "Error! \"$sim_imlist_file\" does not exist! Skip!" >> "log_errors.txt"
        continue
        #exit 255
    fi
    sim_imlist_dir=$(dirname "$sim_imlist_file")
    
    IFS=$'\n' read -d '' -r -a sim_imlist < "../models/$sim_imlist_file"
    
    # 
    # cd sim project dir
    if [[ ! -d "$sim_project_name" ]]; then
        mkdir "$sim_project_name"
    fi
    cd "$sim_project_name"
    
    # 
    # prepare batch script for running a3cosmos-prior-extraction-photometry
    echo "#!/bin/bash" > "do_prior_fitting.sh"
    echo "" >> "do_prior_fitting.sh"
    echo "source $HOME/Cloud/Github/AlmaCosmos/Softwares/SETUP.bash" >> "do_prior_fitting.sh"
    echo "source $HOME/Cloud/Github/AlmaCosmos/Pipeline/SETUP.bash" >> "do_prior_fitting.sh"
    
    # 
    # loop sim image list
    for (( im = 0; im < ${#sim_imlist[@]}; im++ )); do
        # now we get the simulated image file path
        # check if it is empty of not
        if [[ x"${sim_imlist[im]}" = x"" ]]; then
            continue
        fi
        # check if it is an absolution path (starting with "/") or not. If not, then we prepend the "$sim_imlist_dir" path. 
        if [[ "${sim_imlist[im]}" != "/"* ]]; then
            sim_image_file="../${sim_imlist_dir}/${sim_imlist[im]}"
        else
            sim_image_file="${sim_imlist[im]}"
        fi
        sim_model_file=$(echo "$sim_image_file" | sed -e 's/_model\.fits\.gz/_info.save/g')
        sim_image_name=$(basename "$sim_image_file" | sed -e 's/_model\.fits\.gz//g')
        # 
        # check file existance
        echo "sim_image_file = $sim_image_file"
        echo "sim_model_file = $sim_model_file"
        if [[ ! -f "$sim_image_file" ]]; then
            echo "Error! \"$sim_image_file\" does not exist!"
            exit 255
        fi
        if [[ ! -f "$sim_model_file" ]]; then
            echo "Error! \"$sim_model_file\" does not exist!"
            exit 255
        fi
        # 
        # unzip sim image file into "Input_Images" for running a3cosmos-prior-extraction-photometry
        if [[ ! -d "Input_Images" ]]; then
            mkdir "Input_Images"
        fi
        if [[ ! -f "Input_Images/${sim_image_name}_model.fits" ]]; then
            cd "Input_Images"
            echo "gunzip -c \"../$sim_image_file\" > \"${sim_image_name}_model.fits\""
            gunzip -c "../$sim_image_file" > "${sim_image_name}_model.fits"
            cd "../"
        fi
        # 
        # run IDL and prepare sim catalog file into "Input_Catalogs" for running a3cosmos-prior-extraction-photometry
        if [[ ! -d "Input_Catalogs" ]]; then
            mkdir "Input_Catalogs"
        fi
        if [[ ! -f "Input_Catalogs/${sim_image_name}_catalog.txt" ]]; then
            cd "Input_Catalogs"
            echo "running idl to read \"../$sim_model_file\""

idl -quiet << EOF
restore, '../$sim_model_file', verbose=false
sim_x = CENX+1 ; CENX starts from 0, see dist_ellipse.pro
sim_y = CENY+1 ; CENY starts from 0, see dist_ellipse.pro
sim_pixsc = PIXSCL * 3600.0 ; arcsec
;sim_Maj = SOURCE_SIZE * BEAMSIZE_PIX * sim_pixsc # arcsec #<20171229><BUG># SOURCE_SIZE = sim_Size * BEAMSIZE_PIX
sim_Maj = SOURCE_SIZE * sim_pixsc ; arcsec #<20171229><BUG># SOURCE_SIZE = sim_Size * BEAMSIZE_PIX
sim_Min = sim_Maj * AR ; arcsec
sim_PA = PA ; degree
sim_peak_flux = double(PEAK_FLUX) ; Jy/beam
sim_total_flux = double(TOTAL_FLUX) ; Jy
sim_beam_maj = BEAMSIZE_PIX * sim_pixsc ; arcsec
sim_beam_min = BEAMSIZE_MINOR_PIX * sim_pixsc ; arcsec
sim_beam_pa = BEAMPA ; degree
str_pos_1 = strpos('$sim_image_name','Size')+strlen('Size')
str_pos_2 = strpos('$sim_image_name','_SN')
sim_Size = float(strmid('$sim_image_name', str_pos_1, str_pos_2 - str_pos_1))
str_pos_1 = strpos('$sim_image_name','_SN')+strlen('_SN')
str_pos_2 = strpos('$sim_image_name','_number')
sim_SNR_peak = float(strmid('$sim_image_name', str_pos_1, str_pos_2 - str_pos_1))
str_pos_1 = strpos('$sim_image_name','_number')+strlen('_number')
sim_id = fix(strmid('$sim_image_name', str_pos_1))
sim_rms = sim_peak_flux / sim_SNR_peak
sim_image_name = '$sim_image_name'
sim_image_dir = '$sim_project_name'
sim_ra = 0.0D
sim_dec = 0.0D
fits_header = headfits('../Input_Images/${sim_image_name}_model.fits')
extast, fits_header, fits_astro
;CrabImageXY2AD, sim_x, sim_y, '../Input_Images/${sim_image_name}_model.fits', sim_ra, sim_dec
xy2ad, CENX, CENY, fits_astro, sim_ra, sim_dec
CrabTablePrintC, '${sim_image_name}_catalog.txt', sim_id, sim_ra, sim_dec, sim_Maj, sim_Min, sim_PA, sim_beam_maj, sim_beam_min, sim_beam_pa, sim_peak_flux, sim_total_flux, sim_rms, sim_Size, sim_SNR_peak, sim_image_dir, sim_image_name
EOF

            cd "../"
        fi
        # 
        # get image rms and fake a image pixel rms txt file
        if [[ ! -f "Input_Images/${sim_image_name}_model.fits.pixel.statistics.txt" ]]; then
            Gaussian_sigma=$(cat "Input_Catalogs/${sim_image_name}_catalog.txt" | grep -v '^#' | head -n 1 | sed -e 's/^ *//g' | tr -s ' ' | cut -d ' ' -f 12)
            if [[ x"$Gaussian_sigma" != x"" ]]; then
                echo "Gaussian_sigma = $Gaussian_sigma" > "Input_Images/${sim_image_name}_model.fits.pixel.statistics.txt"
                echo "Inner_sigma = $Gaussian_sigma" >> "Input_Images/${sim_image_name}_model.fits.pixel.statistics.txt"
            else
                echo "Error! Failed to get Gaussian_sigma from \"Input_Catalogs/${sim_image_name}_catalog.txt\"! Exit!"
                exit 255
            fi
        fi
        # 
        # prepare batch script for running a3cosmos-prior-extraction-photometry
        echo "" >> "do_prior_fitting.sh"
        echo "a3cosmos-prior-extraction-photometry \\" >> "do_prior_fitting.sh"
        echo "              -cat \"Input_Catalogs/${sim_image_name}_catalog.txt\" \\" >> "do_prior_fitting.sh"
        echo "              -sci \"Input_Images/${sim_image_name}_model.fits\" \\" >> "do_prior_fitting.sh"
        echo "              -output-dir \"Output_Photometry\" \\" >> "do_prior_fitting.sh"
        echo "              -output-name \"${sim_image_name}\" \\" >> "do_prior_fitting.sh"
        echo "              -steps getpix galfit gaussian final " >> "do_prior_fitting.sh"
        echo "" >> "do_prior_fitting.sh"
        
    done
    
    # 
    # now finish the preparation
    date "%Y-%m-%d %H:%M:%S %Z" > "do_prior_fitting.sh.ok"
    
    # 
    # cd back
    cd "../"
    
    # 
    # debug break
    #break
    
done


