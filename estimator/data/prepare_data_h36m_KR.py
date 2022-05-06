# Copyright (c) 2018-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import argparse
import os
import zipfile
import numpy as np
import h5py
from glob import glob
from shutil import rmtree

import sys
sys.path.append('../')
from common.h36m_dataset import Human36mDataset
from common.camera import world_to_camera, project_to_2d, image_coordinates
from common.utils import wrap

output_filename = 'data_KRtest_3d_h36m'
output_filename_2d = 'data_KRtest_2d_h36m_gt'
subjects = ['S1', 'S5', 'S6', 'S7', 'S8', 'S9', 'S11']

if __name__ == '__main__':
    if os.path.basename(os.getcwd()) != 'data':
        print('This script.sh must be launched from the "data" directory')
        exit(0)
        
    parser = argparse.ArgumentParser(description='Human3.6M dataset downloader/converter')
    
    # Convert dataset preprocessed by Martinez et al. in https://github.com/una-dinosauria/3d-pose-baseline
    parser.add_argument('--from-archive', default='', type=str, metavar='PATH', help='convert preprocessed dataset')
    
    # Convert dataset from original source, using files converted to .mat (the Human3.6M dataset path must be specified manually)
    # This option requires MATLAB to convert files using the provided script.sh
    parser.add_argument('--from-source', default='', type=str, metavar='PATH', help='convert original dataset')
    
    # Convert dataset from original source, using original .cdf files (the Human3.6M dataset path must be specified manually)
    # This option does not require MATLAB, but the Python library cdflib must be installed
    parser.add_argument('--from-source-cdf', default='', type=str, metavar='PATH', help='convert original dataset')
    
    args = parser.parse_args()
    
    if args.from_archive and args.from_source:
        print('Please specify only one argument')
        exit(0)
    
    if os.path.exists(output_filename + '.npz'):
        print('The dataset already exists at', output_filename + '.npz')
        # exit(0)
        


    if args.from_source_cdf:
        print('Converting original Human3.6M dataset from', args.from_source_cdf, '(CDF files)')
        output = {}
        
        import cdflib
        
        for subject in subjects:
            output[subject] = {}
            file_list = glob(args.from_source_cdf + '/' + subject + '/MyPoseFeatures/D3_Positions/*.cdf')
            # file_list = glob(args.from_source_cdf + '/' + subject + '/MyPoseFeatures/D3_Angles/*.cdf')
            assert len(file_list) == 30, "Expected 30 files for subject " + subject + ", got " + str(len(file_list))
            for f in file_list:
                action = os.path.splitext(os.path.basename(f))[0]
                
                if subject == 'S11' and action == 'Directions':
                    continue # Discard corrupted video
                    
                # Use consistent naming convention
                canonical_name = action.replace('TakingPhoto', 'Photo') \
                                       .replace('WalkingDog', 'WalkDog')
                
                hf = cdflib.CDF(f)
                positions = hf['Pose'].reshape(-1, 32, 3)
                positions /= 1000 # Meters instead of millimeters
                output[subject][canonical_name] = positions.astype('float32')
        
        print('Saving...')
        np.savez_compressed(output_filename, positions_3d=output)
        
        print('Done.')
            
    else:
        print('Please specify the dataset source')
        exit(0)
        
    # Create 2D pose file
    print('')
    print('Computing ground-truth 2D poses...')
    dataset = Human36mDataset(output_filename + '.npz')
    output_2d_poses = {}
    for subject in dataset.subjects():
        output_2d_poses[subject] = {}
        for action in dataset[subject].keys():
            anim = dataset[subject][action]
            
            positions_2d = []
            for cam in anim['cameras']:
                pos_3d = world_to_camera(anim['positions'], R=cam['orientation'], t=cam['translation'])
                pos_2d = wrap(project_to_2d, pos_3d, cam['intrinsic'], unsqueeze=True)
                pos_2d_pixel_space = image_coordinates(pos_2d, w=cam['res_w'], h=cam['res_h'])
                positions_2d.append(pos_2d_pixel_space.astype('float32'))
            output_2d_poses[subject][action] = positions_2d
            
    print('Saving...')
    metadata = {
        'num_joints': dataset.skeleton().num_joints(),
        'keypoints_symmetry': [dataset.skeleton().joints_left(), dataset.skeleton().joints_right()]
    }
    np.savez_compressed(output_filename_2d, positions_2d=output_2d_poses, metadata=metadata)
    
    print('Done.')
