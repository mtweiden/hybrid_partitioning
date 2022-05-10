echo "mult_16"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-mult_16_mesh.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-mult_16_mesh.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/lines-no_synth-qft_64_mesh.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/lines-qft_64_mesh.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/lines-no_synth-add_65_mesh.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/lines-add_65_mesh.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/lines-no_synth-hubbard_18_mesh.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/lines-hubbard_18_mesh.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-shor_26_mesh.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-shor_26_mesh.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-tfim_40_mesh.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/lines-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-tfim_40_mesh.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-mult_16_mesh.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-mult_16_mesh.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/stars-no_synth-qft_64_mesh.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/stars-qft_64_mesh.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/stars-no_synth-add_65_mesh.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/stars-add_65_mesh.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/stars-no_synth-hubbard_18_mesh.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/stars-hubbard_18_mesh.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-shor_26_mesh.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-shor_26_mesh.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-tfim_40_mesh.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/stars-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-tfim_40_mesh.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-mult_16_mesh.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-mult_16_mesh.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/rings-no_synth-qft_64_mesh.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/rings-qft_64_mesh.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/rings-no_synth-add_65_mesh.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/rings-add_65_mesh.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/rings-no_synth-hubbard_18_mesh.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/rings-hubbard_18_mesh.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-shor_26_mesh.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-shor_26_mesh.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-tfim_40_mesh.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/rings-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-tfim_40_mesh.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-mult_16_mesh.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-mult_16_mesh.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/kites-no_synth-qft_64_mesh.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/kites-qft_64_mesh.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/kites-no_synth-add_65_mesh.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/kites-add_65_mesh.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/kites-no_synth-hubbard_18_mesh.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/kites-hubbard_18_mesh.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-shor_26_mesh.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-shor_26_mesh.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-tfim_40_mesh.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/kites-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-tfim_40_mesh.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-mult_16_mesh.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-mult_16_mesh.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/thetas-no_synth-qft_64_mesh.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/thetas-qft_64_mesh.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/thetas-no_synth-add_65_mesh.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/thetas-add_65_mesh.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/thetas-no_synth-hubbard_18_mesh.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/thetas-hubbard_18_mesh.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-shor_26_mesh.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-shor_26_mesh.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-tfim_40_mesh.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/thetas-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-tfim_40_mesh.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-mult_16_mesh.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-mult_16_mesh.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/alls-no_synth-qft_64_mesh.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/alls-qft_64_mesh.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/alls-no_synth-add_65_mesh.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/alls-add_65_mesh.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/alls-no_synth-hubbard_18_mesh.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/alls-hubbard_18_mesh.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-shor_26_mesh.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-shor_26_mesh.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-tfim_40_mesh.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology mesh --blocksize 4 qasm/alls-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-tfim_40_mesh.csv


echo "mult_16"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-mult_16_falcon.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-mult_16_falcon.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/lines-no_synth-qft_64_falcon.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/lines-qft_64_falcon.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/lines-no_synth-add_65_falcon.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/lines-add_65_falcon.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/lines-no_synth-hubbard_18_falcon.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/lines-hubbard_18_falcon.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-shor_26_falcon.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-shor_26_falcon.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-tfim_40_falcon.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/lines-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-tfim_40_falcon.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-mult_16_falcon.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-mult_16_falcon.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/stars-no_synth-qft_64_falcon.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/stars-qft_64_falcon.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/stars-no_synth-add_65_falcon.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/stars-add_65_falcon.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/stars-no_synth-hubbard_18_falcon.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/stars-hubbard_18_falcon.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-shor_26_falcon.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-shor_26_falcon.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-tfim_40_falcon.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/stars-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-tfim_40_falcon.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-mult_16_falcon.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-mult_16_falcon.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/rings-no_synth-qft_64_falcon.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/rings-qft_64_falcon.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/rings-no_synth-add_65_falcon.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/rings-add_65_falcon.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/rings-no_synth-hubbard_18_falcon.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/rings-hubbard_18_falcon.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-shor_26_falcon.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-shor_26_falcon.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-tfim_40_falcon.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/rings-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-tfim_40_falcon.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-mult_16_falcon.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-mult_16_falcon.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/kites-no_synth-qft_64_falcon.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/kites-qft_64_falcon.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/kites-no_synth-add_65_falcon.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/kites-add_65_falcon.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/kites-no_synth-hubbard_18_falcon.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/kites-hubbard_18_falcon.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-shor_26_falcon.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-shor_26_falcon.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-tfim_40_falcon.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/kites-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-tfim_40_falcon.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-mult_16_falcon.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-mult_16_falcon.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/thetas-no_synth-qft_64_falcon.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/thetas-qft_64_falcon.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/thetas-no_synth-add_65_falcon.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/thetas-add_65_falcon.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/thetas-no_synth-hubbard_18_falcon.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/thetas-hubbard_18_falcon.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-shor_26_falcon.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-shor_26_falcon.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-tfim_40_falcon.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/thetas-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-tfim_40_falcon.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-mult_16_falcon.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-mult_16_falcon.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/alls-no_synth-qft_64_falcon.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/alls-qft_64_falcon.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/alls-no_synth-add_65_falcon.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/alls-add_65_falcon.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/alls-no_synth-hubbard_18_falcon.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/alls-hubbard_18_falcon.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-shor_26_falcon.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-shor_26_falcon.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-tfim_40_falcon.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology falcon --blocksize 4 qasm/alls-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-tfim_40_falcon.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-mult_16_linear.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-mult_16_linear.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/lines-no_synth-qft_64_linear.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/lines-qft_64_linear.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/lines-no_synth-add_65_linear.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/lines-add_65_linear.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/lines-no_synth-hubbard_18_linear.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/lines-hubbard_18_linear.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-shor_26_linear.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-shor_26_linear.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/lines-no_synth-tfim_40_linear.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/lines-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/lines-tfim_40_linear.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-mult_16_linear.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-mult_16_linear.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/stars-no_synth-qft_64_linear.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/stars-qft_64_linear.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/stars-no_synth-add_65_linear.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/stars-add_65_linear.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/stars-no_synth-hubbard_18_linear.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/stars-hubbard_18_linear.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-shor_26_linear.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-shor_26_linear.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/stars-no_synth-tfim_40_linear.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/stars-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/stars-tfim_40_linear.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-mult_16_linear.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-mult_16_linear.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/rings-no_synth-qft_64_linear.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/rings-qft_64_linear.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/rings-no_synth-add_65_linear.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/rings-add_65_linear.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/rings-no_synth-hubbard_18_linear.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/rings-hubbard_18_linear.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-shor_26_linear.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-shor_26_linear.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/rings-no_synth-tfim_40_linear.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/rings-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/rings-tfim_40_linear.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-mult_16_linear.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-mult_16_linear.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/kites-no_synth-qft_64_linear.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/kites-qft_64_linear.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/kites-no_synth-add_65_linear.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/kites-add_65_linear.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/kites-no_synth-hubbard_18_linear.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/kites-hubbard_18_linear.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-shor_26_linear.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-shor_26_linear.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/kites-no_synth-tfim_40_linear.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/kites-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/kites-tfim_40_linear.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-mult_16_linear.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-mult_16_linear.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/thetas-no_synth-qft_64_linear.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/thetas-qft_64_linear.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/thetas-no_synth-add_65_linear.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/thetas-add_65_linear.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/thetas-no_synth-hubbard_18_linear.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/thetas-hubbard_18_linear.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-shor_26_linear.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-shor_26_linear.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/thetas-no_synth-tfim_40_linear.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/thetas-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/thetas-tfim_40_linear.csv

echo "mult_16"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-mult_16_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-mult_16_linear.csv
echo "mult_16 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-mult_16_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-mult_16_linear.csv
echo "qft_64"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-qft_64_preoptimized.qasm                        >> csv_files/paper_measurements/alls-no_synth-qft_64_linear.csv
echo "qft_64 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-qft_64_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/alls-qft_64_linear.csv
echo "add_65"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-add_65_preoptimized.qasm                        >> csv_files/paper_measurements/alls-no_synth-add_65_linear.csv
echo "add_65 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-add_65_preoptimized.qasm --synthesis_impact     >> csv_files/paper_measurements/alls-add_65_linear.csv
echo "hubbard_18"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-hubbard_18_preoptimized.qasm                    >> csv_files/paper_measurements/alls-no_synth-hubbard_18_linear.csv
echo "hubbard_18 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-hubbard_18_preoptimized.qasm --synthesis_impact >> csv_files/paper_measurements/alls-hubbard_18_linear.csv
echo "shor_26"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-shor_26_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-shor_26_linear.csv
echo "shor_26 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-shor_26_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-shor_26_linear.csv
echo "tfim_40"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-tfim_40_preoptimized.qasm                       >> csv_files/paper_measurements/alls-no_synth-tfim_40_linear.csv
echo "tfim_40 synth"
python measure_impact.py --partitioner scan --topology linear --blocksize 4 qasm/alls-tfim_40_preoptimized.qasm --synthesis_impact    >> csv_files/paper_measurements/alls-tfim_40_linear.csv