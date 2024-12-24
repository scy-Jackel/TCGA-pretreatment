# TCGA-pretreatment
 
Open cmd, enter the folder where TCGA data needs to be stored, move gdc-client. exe and gdc_manifest.txt to this folder, and execute gdc-client.exe download - m gdc_manifest.txt on the command line to download TCGA data.


RGB_split.py splits TCGA data into 448 * 448 subgraphs.


scaling-ndpi.py shrinks the pathological slices in ndpi format to a size of 4000 * 3000.


scaling_svs.py shrinks the pathological slices in svs format to a size of 4000 * 3000.
