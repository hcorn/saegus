%%cmd
cd C:\GWAS\tassel-5-standalone
run_pipeline.bat -fork1 -h C:\Users\DoubleDanks\Dropbox\wgs-and-beyond\gwas\simulator_results\input\run_4_sim_hapmap.txt -fork2 -t C:\Users\DoubleDanks\Dropbox\wgs-and-beyond\gwas\simulator_results\input\run_4_sim_trait_vector.txt  -fork3 -q C:\Users\DoubleDanks\Dropbox\wgs-and-beyond\gwas\simulator_results\input\run_4_sim_structure.txt -fork4 -k C:\Users\DoubleDanks\Dropbox\wgs-and-beyond\gwas\simulator_results\input\run_4_sim_kinship.txt -combine5 -input1 -input2 -input3 -intersect -combine6 -input5 -input4 -mlm -mlmCompressionLevel None -export C:\Users\DoubleDanks\Dropbox\wgs-and-beyond\gwas\simulator_results\output\sim_run_4 -runfork1 -runfork2 -runfork3 -runfork4