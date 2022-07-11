#!/bin/bash


bold=$(tput bold)
normal=$(tput sgr0)
GIT_REPO='https://github.com/deepmind/alphafold'
SOURCE_URL='https://storage.googleapis.com/alphafold/alphafold_params_colab_2022-01-19.tar'
SOURCE_URL_V2='https://storage.googleapis.com/alphafold/alphafold_params_2022-03-02.tar'
PARAMS_DIR='./alphafold/data/params'

py_script="
import sys
import os
first = sys.argv[1]
second = sys.argv[2]
print(os.path.join(first, os.path.basename(second)))
"

PARAMS_PATH=$(python -c "$py_script" ${PARAMS_DIR} ${SOURCE_URL})
PARAMS_PATH_V2=$(python -c "$py_script" ${PARAMS_DIR} ${SOURCE_URL_V2})

# =============================================================================
# 1. Install dependencies
# See the acknowledgements on
# https://github.com/deepmind/alphafold/#acknowledgements
# in AF2 readme for the list of software.
# =============================================================================

echo "${bold}Progress:  5%${normal}"
echo "Uninstalling current version of tensorflow..."
pip uninstall -y tensorflow

echo "${bold}Progress:  10%${normal}"
echo "Installing hmmer..."
apt install -y hmmer
rm -rf /opt/conda

echo "${bold}Progress:  15%${normal}"
echo "Installing the latest version of Miniconda..."
wget -q -P /tmp https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        && sudo cp /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda/ \
        && rm /tmp/Miniconda3-latest-Linux-x86_64.sh
echo 'export PATH=/opt/conda/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

echo "${bold}Progress:    20%${normal}"
echo "Updating of the conda & python..."
conda update -q -y conda && conda install -q -y -c conda-forge python=3.7
mkdir -m 777 --parents /tmp/ramdisk
mount -t tmpfs -o size=9G ramdisk /tmp/ramdisk

echo "${bold}Progress:  30%${normal}"
echo "Installing stereo_chemical_props.txt from Git..."
wget -q -P /content https://git.scicore.unibas.ch/schwede/openstructure/-/raw/\
7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt

# =============================================================================
# 2. Download AlphaFold
# =============================================================================

sudo rm -rf alphafold

echo "${bold}Progress:  40%${normal}"
echo "Clonning AlphaFold from Git..."
git clone -q --branch main ${GIT_REPO} alphafold && cd alphafold \
      && git checkout 57a2455e5fab752d8df430ae1d0334e1a21b548c && cd ..
      #&& git checkout 918434f597c0f8a7bd999f878de474aeb0a0b4ae && cd ..
# TODO: make the actual commit optional

echo "${bold}Progress:  50%${normal}"
echo "Installing the required versions of all dependencies..."
pip3 install -q -r ./alphafold/requirements.txt
# Run setup.py to install only AlphaFold.
# pip3 install --no-dependencies ./alphafold

echo "${bold}Progress:  60%${normal}"
echo "Apply OpenMM patch..."
# Apply OpenMM patch.
#    pushd /opt/conda/lib/python3.7/site-packages/ && \
#    patch -p0 < /content/alphafold/docker/openmm.patch && \
#    popd

      # Make sure stereo_chemical_props.txt is in all locations where it could be searched for.
mkdir -p /content/alphafold/alphafold/common
cp -f /content/stereo_chemical_props.txt /content/alphafold/alphafold/common
mkdir -p /opt/conda/lib/python3.7/site-packages/alphafold/common/
cp -f /content/stereo_chemical_props.txt /opt/conda/lib/python3.7/site-packages/alphafold/common/

echo "${bold}Progress:  70%${normal}"

mkdir --parents ${PARAMS_DIR}
wget -q -O ${PARAMS_PATH} ${SOURCE_URL}
tar --extract --verbose --file=${PARAMS_PATH} \
    --directory=${PARAMS_DIR} --preserve-permissions
rm ${PARAMS_PATH}

echo "${bold}Progress:  80%${normal}"

wget -O ${PARAMS_PATH_V2} ${SOURCE_URL_V2}

tar --extract --verbose --file=${PARAMS_PATH_V2} \
    --directory=${PARAMS_DIR} --preserve-permissions
rm ${PARAMS_PATH_V2}

echo "${bold}Success!${normal}"
# =============================================================================
#
# =============================================================================
PARAMS_DIR='./alphafold/data'
# =============================================================================
#
# =============================================================================
WRAPPER_REPO='https://bitbucket.org/abc-group/af2_wrapper.git'
git clone --branch master ${WRAPPER_REPO} af2_wrapper && cd af2_wrapper \
      && git checkout e4a048542102cb97040a414c3831ce18a98647ec && cd ..
# =============================================================================
#
# =============================================================================
pip install --upgrade "jax[cuda]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

