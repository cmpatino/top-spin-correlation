# 1. Run Container
1. sudo docker run -it hep-sw

# 2. Open MadGraph5
1. mg5_aMC

# 3a. Run event generation for SM
1. generate p p > t t~
2. launch -m
3. Activate Pythia, Delphes, and MadSpin
4. Set quark mass to 172.5 GeV on param card.
5. Set seed and number of events on run card.
6. Change madspin card (seed and decays).

# 3b. Run event generation for EFT
1. import model dim6top_LO_UFO
2. generate p p > t t~
3. launch -m
4. Activate Pythia, Delphes, and MadSpin
5. Set quark mass to 172.5 GeV on param card.
6. Set seed and number of events on run card
7. Change madspin card (seed and decays).

# 4. Save events to host
1. sudo docker container ls
2. sudo docker cp <containerId>:/file/path/in/container/file /host/local/path/file
    + File of interest is the one in `Events/`