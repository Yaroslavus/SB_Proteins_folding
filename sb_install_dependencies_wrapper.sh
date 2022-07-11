#!/bin/bash

sudo ./sb_install_dependencies_1.sh 1> >(tee .sb_stdout.log) 2> >(tee .sb_stderr.log)
