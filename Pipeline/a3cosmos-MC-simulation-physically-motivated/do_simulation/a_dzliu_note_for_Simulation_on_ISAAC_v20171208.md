### login ISAAC machine
```
ssh -A -t dzliu@gate.rzg.mpg.de ssh -A -t isaac1.bc.rzg.mpg.de
```

### git
```
mdkir -p ~/Cloud/Github
cd ~/Cloud/Github
module load git
git clone https://github.com/1054/AlmaCosmos.git
```

### sm
```
mkdir -p ~/Softwares/Supermongo
cd ~/Softwares/Supermongo
unzip ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/Supermo_bck.zip
rm -r Supermongo_macro
ln -fs ~/Cloud/Github/DeepFields.SuperDeblending/Softwares/Supermongo_macro
```

### gdio
```
scp ~/.almacosmos/CAAP*.json remote:~/.almacosmos/
```

### cd
```
cd ~/Work/AlmaCosmos/Photometry/ALMA_full_archive/Simulation_by_Daizhong/
```

### re-do all recover steps with my new galfit macros -- ......
```
rm -rf Simulated/ Recovered/
```

### do Step_1 Prepare
```
~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_1_Prepare.sh
```

### do Step_2 Simulate
```
sbatch --array=1-4%4 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_2_Simulate.sh # Submitted batch job 44497, 01h45m, 06h53m
squeue
sacct -j 44497 --format=state,elapsed,nnodes,ncpus,nodelist,ReqMem,MaxVMSize,AveVMSize,AveCPU,AveCPUFreq,AllocCPUS,job

sbatch --array=5-89%6 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_2_Simulate.sh # Submitted batch job 44515, 06h54m
sacct -j 44515 --format=state,elapsed,nnodes,ncpus,nodelist,ReqMem,MaxVMSize,AveVMSize,AveCPU,AveCPUFreq,AllocCPUS,job
```

### do Step_3 Recover
```
sbatch --array=1-1%1 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_3_Recover.sh # 44620, used 4h30min

ls Recovered/2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3/w_876.764_z_1.000_lgMstar_10.50_SB/astrodepth_prior_extraction_photometry/image_sim.cut_321_321_702_702/

tail -n 30 Recovered/2011.0.00097.S_SB1_GB1_MB10_COSMOS6_field2_sci.spw0_1_2_3/w_876.764_z_1.000_lgMstar_10.50_SB/astrodepth_prior_extraction_photometry/image_sim.cut_321_321_702_702/fit_2.out

sbatch --array=2-24%4 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_3_Recover.sh # Submitted batch job 44664

sbatch --array=25-89%4 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_3_Recover.sh # Submitted batch job 44720, 2017-12-13, 02h03m, 

sbatch --array=1-89%4 -N1 ~/Cloud/Github/AlmaCosmos/Pipeline/a3cosmos-MC-simulation-physically-motivated/do_simulation/a_dzliu_code_for_Simulation_on_ISAAC_Step_3_Recover_with_8GB_memory.sh # Submitted batch job 45180, 2017-12-22, 13h38m, 
```

### check slurm system status
```
squeue
sacct -j 45180 --format=state,elapsed,nnodes,ncpus,nodelist,ReqMem,MaxVMSize,AveVMSize,AveCPU,AveCPUFreq,AllocCPUS,job
```

### check logs
```
ls -v
ls -alt | head -n 10
tail -n 30 log_Step_3_TASK_ID_14_JOB_ID_45180.out
```

### cancel slurm task
```
scancel 45180
```


