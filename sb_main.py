#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 20:55:06 2021

@author: yaroslav
"""

import sb_tools
#import os
import subprocess
import tqdm.notebook
#import pandas as pd

# =============================================================================
# 3. SEQUENCE INPUTS
# Specify query sequences and corresponding chain names.
# You can specify more than one chain id to indicate that the protein is a homomultimer.
# =============================================================================

protein_1_sequence = 'APARSPSPSTQPWEHVNAIQEARRLLNLSRDTAAEMNETVEVISEMFDLQEPTCLQTRLELYKQGLRGSLTKLKGPLTMMASHYKQHCPPTPETSCATQIITFESFKENLKDFLLVIPFDCWEPVQE'  #@param {type:"string"}
protein_1_chains = 'C' #@param {type:"string"}
protein_2_sequence = 'EVKLQQSGPELVKPGASVKISCKASGYSFTNYYMHWMKQRPGQGLEWIGWIFPGSDNTKYNEKFKGKATLTADTSSSTAYMQLSSLTSEDSAVYFCARKGTTGFAYWGQGTLVTV'  #@param {type:"string"}
protein_2_chains = 'H' #@param {type:"string"}
protein_3_sequence = 'DIQLTQSPSSLSASLGDTITITCHASQNINVWLSWYQQKPGNIPKLLIYKASNLHTGVPSRFSGSGSGTGFTLTISSLQPEDIATYYCQQGQSYPLTFGGGTKLEI'  #@param {type:"string"}
protein_3_chains = 'L' #@param {type:"string"}
protein_4_sequence = ''  #@param {type:"string"}
protein_4_chains = '' #@param {type:"string"}

names_list = ['protein_1', 'protein_2', 'protein_3', 'protein_4']
sequences_list = [protein_1_sequence, protein_2_sequence, protein_3_sequence, protein_4_sequence]
chains_list = [protein_1_chains, protein_2_chains, protein_3_chains, protein_4_chains]

sequence_data = []
all_chains_list = []
for name, seq, chains in zip(names_list, sequences_list, chains_list):
    if seq != '':
        chains_list = [chain for chain in chains]
        sequence_data.append({'name': name, 'sequence': seq, 'chains': chains_list})
        all_chains_list += chains_list

query_seq_dict = {seq_data['name']: seq_data['sequence'] for seq_data in sequence_data}
chain_names = ''.join(all_chains_list)
# =============================================================================
# 4. STRUCTURAL INPUTS
# Upload structural models to be refined and rescored.
# PDB files, and zip or tar.bz2 archives containing PDB files are accepted.
# These models should have the same sequences and chain names as query sequences above,
# but may have missing regions, which will be rebuilt.
# Uncheck **delete_existing_files** to retain the files genereated during previous runs of this cell.
# =============================================================================

delete_existing_files = True #@param {type:"boolean"} 

if delete_existing_files:
    subprocess.call(["rm", "-rf", "uploads_tmp*", "pdb_folder*", "uploads*"])

import os
import shutil
from glob import glob
from google.colab import files

uploaded_files = files.upload()
    
#assert len(zip_file.keys()) == 1 , 'the number of zip file is more than one'
uploads_dir = 'uploads'
tmp_dir = 'uploads_tmp'
pdb_dir = 'pdb_folder'
subprocess.call(["mkdir", "-p", "$uploads_dir"])
subprocess.call(["mkdir", "-p", "$tmp_dir"])
subprocess.call(["mkdir", "-p", "$pdb_dir"])

for fname in uploaded_files.keys():
    subprocess.call(["mv", "./{fname}", "./{uploads_dir}/{fname}"])
    cur_file_path = os.path.join('.',uploads_dir,fname)
    fbase, fext = os.path.splitext(fname)
    #tmp_folder = os.path.join('.','tmp_pdb_folder')
    if fext == '.zip':
        subprocess.call(["unzip", "$cur_file_path", "-d", "{tmp_dir}"])
    elif fext == '.bz2':
        subprocess.call(["tar", "-xf", "$cur_file_path", "-C", "{tmp_dir}"])
    elif fext == '.pdb':
        subprocess.call(["cp", "$cur_file_path", "{tmp_dir}/"])

pdbs_new = []
for root,dirs,files in os.walk(tmp_dir):
    for basename in files:
        fbase, fext = os.path.splitext(basename)
        if fext == '.pdb':
            pdb_path_old = os.path.join(root, basename)
            pdb_path_new = os.path.join(pdb_dir, basename)
            shutil.copy(pdb_path_old, pdb_path_new)
            pdbs_new.append(pdb_path_new)

'''
list_of_all_pdb_path = []
for dir,_,_ in os.walk():
    list_of_all_pdb_path.extend(glob(os.path.join(dir,"*.pdb")))

%shell mkdir --parents "pdb_folder"
pdbs_new = []
for pdb_fname in list_of_all_pdb_path:
    basename = os.path.basename(pdb_fname)
    pdb_fname_new = os.path.join('pdb_folder', basename)
    shutil.copy(pdb_fname, pdb_fname_new)
    pdbs_new.append(pdb_fname_new)
'''
templates  = []
for pdb_fname in sorted(pdbs_new):
    templates.append({'pdb_file': pdb_fname, "mapping_method": "custom"})
#print(list_of_all_pdb_path)
    
# =============================================================================
# 5. GENERATE MSAs
# Run HMMER to generate multiple sequence alignments.
# Following the original AF2 colab, the search is performed on chunks of the standard AF2 sequence databases.
# The standard mode is the default, while the minimalistic mode further restricts the databases,
# and should be used for debug only.
# =============================================================================

mode = 'minimalistic' #@param ["standard", "minimalistic"]
is_debug = True if mode == "minimalistic" else False
from af2tmplt.msa_std import get_MSAs_googleapi
query_seq_to_msa = get_MSAs_googleapi(query_seq_dict, output_path='./', debug=is_debug)
# =============================================================================
# 6. RUN AF2
# Run AF2 to refine and rescore the models.
# You can select which version of AF2 parameters to use.
# Uncheck **delete_existing_files** to retain the files genereated during previous runs of this cell.
# (files generated with the same job_name and parameter_set will be overwritten in any case)
# =============================================================================

job_name = "test" #@param {type:"string"}
parameter_set = 'monomer_ptm' #@param ["multimer", "multimer_v2", "monomer_ptm"]
delete_existing_files = True #@param {type:"boolean"} 

if delete_existing_files:
    subprocess.call(["rm", "-f", "*.pdb", "*.pkl", "*.csv"])

import csv

from alphafold.data import feature_processing
from alphafold.model import model
from alphafold.common import protein

from af2tmplt import global_var
global_var.MODEL_SET = parameter_set
from af2tmplt.featurize import build_feature_dict_default
from af2tmplt.predict import get_confidence_metrics
from af2tmplt.predict import predict_structure_tmplt

protein.PDB_CHAIN_IDS = ('-') + ''.join(chain_names)
feature_processing.MAX_TEMPLATES = 1
model.get_confidence_metrics = get_confidence_metrics

print(f"{'Template_pdb' : <40} {'Refined_pdb' : <40} {'Multimer confidence score' : <10}")
for i, template in enumerate(templates):
    #for i, template in enumerate([None]):
    feature_dict =  build_feature_dict_default(
                                sequence_data,
                                query_seq_to_msa,
                                custom_template = template)
    file_suffix = '' if template == None else '.tmplt_{}'.format(i)
    features_fname = 'features{}.pkl'.format(file_suffix) 
    #with open(features_fname, 'wb') as f:
    #    pickle.dump(feature_dict, f)

    #with open(features_fname, 'rb') as f:
    #    feature_dict = pickle.load(f)

    template_name = None if template == None else template['pdb_file']
    predict_structure_tmplt(feature_dict,
                            job_name + file_suffix,
                            PARAMS_DIR,
                            1,
                            custom_template_name=template_name)
    with open(f'{job_name}{file_suffix}.{global_var.MODEL_SET}.confidence_scores.csv', 'r') as f:
      csv_reader = csv.reader(f)
      firstrow = True
      for row in csv_reader:
        if firstrow:
          firstrow = False
          continue
        model_name = row[0]
        score = float(row[1])
        orig = row[2]
        refined = row[3]
        print(f"{orig : <40} {refined : <40} {score : >.4f}")
# =============================================================================
# 7. DISPLAY RESULTS
# Display a table of resulting scores and refined models.
# =============================================================================

import pandas as pd
from google.colab import data_table
data_table.enable_dataframe_formatter()

allrows = []
fnames = glob(f'{job_name}*.confidence_scores.csv')
for fname in fnames:
    if not os.path.isfile(fname):
        continue
    with open(fname, 'r') as f:
        csv_reader = csv.reader(f)
        firstrow = True
        for row in csv_reader:
            if firstrow:
                firstrow = False
                continue
            allrows.append(row)
data = pd.DataFrame(allrows, columns=['AF2_model', 'Multimer_confidence_score', 'Template_pdb', 'Refined_pdb'])
data.to_csv('confidence_scores.all.csv')
data
# =============================================================================
# 8. DOWNLOAD RESULTS
# Download refined models and scores.
# =============================================================================

subprocess.call(["rm", "-f", "./job_{job_name}.zip"])
subprocess.call(["zip", "./job_{job_name}.zip", "./{job_name}.*.pdb", "./{job_name}.*.pkl", "./{job_name}.*.csv", "./confidence_scores.all.csv"])
files.download(f"./job_{job_name}.zip")
