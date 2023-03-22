echo "####################################"
echo "Generating spectra with a seed 50"
hallucinator -q generate --seed 50 -e V -e Cu -e Co  --noise .5 --peak-width 30 -n 1 --output output/spectra_0
md5sum output/spectra_0/spectra_0.json
echo "####################################"
echo "Generating spectra with same arguments"
hallucinator -q generate --seed 50 -e V -e Cu -e Co  --noise .5 --peak-width 30 -n 1 --output output/spectra_1
md5sum output/spectra_1/spectra_0.json
echo "####################################"
echo "Generating spectra from config"
hallucinator -q generate --config output/spectra_0/hallucination_parameters.json --output output/spectra_2
md5sum output/spectra_2/spectra_0.json
echo "####################################"
echo "Generating spectra from config with different seed"
hallucinator -q generate --seed 65 -e V -e Cu -e Co  --noise .5 --peak-width 30 -n 1 --output output/spectra_3
md5sum output/spectra_3/spectra_0.json
echo "####################################"
hallucinator compare-spectra output/spectra_0/spectra_0.json output/spectra_1/spectra_0.json output/spectra_2/spectra_0.json output/spectra_3/spectra_0.json

