#!/bin/bash
#

BIN_SETUP_FOLDER=$(dirname "${BASH_SOURCE[0]}")
BIN_SETUP_SCRIPT=$(dirname "${BASH_SOURCE[0]}")/bin_setup.bash

source "$BIN_SETUP_SCRIPT" -check a3cosmos-prior-extraction-photometry


