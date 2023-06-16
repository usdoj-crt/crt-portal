#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

echo "This will:"
echo "- Deploy a worker to sandbox."
echo "- Curl the worker."
echo "- Tear everything down."
echo
read -p "If that's what you want, press enter..."
echo
echo "Running deployment..."
./deploy.sh
echo
echo "Deployment complete, proof next:"
echo
./run_proof.sh
echo
read -p "Proof complete, press enter to tear down (or ctrl-c to skip)..."
./teardown.sh
echo
echo "Done!"
