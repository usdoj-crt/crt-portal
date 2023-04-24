echo "Testing read/write configuration between workers and DB."
echo
echo "Worker 1 will be checked first, and will have read/write access."
echo "It will create the database, grant access to worker 2, and do a read test."
echo
echo "Worker 2 will be checked second, and will have read-only access."
echo "It will try to do all of the same things as worker 1, but only be allowed"
echo "to read."
echo ""
echo "Here's that, but in a diagram:"
echo ""
echo "+------------+           +---------+"
echo "|  Worker 1  |   write   |         |"
echo "|   (Main)   |<--------->|         |"
echo "+------------+           |Database |"
echo "                         |(aws-rds)|"
echo "+------------+           |         |"
echo "|  Worker 2  |   read    |         |"
echo "| (Analytics)|<----------+         |"
echo "+------------+           +---------+"
echo ""
read -p "...Press enter to start the test..."
echo ""
echo "Checking database access for worker1:"
cf ssh crt-portal-sandbox-worker1 -c './app/run_proof_remote.sh'
echo
echo "Everything above should have passed."
echo
echo "Checking database access for worker2:"
cf ssh crt-portal-sandbox-worker2 -c './app/run_proof_remote.sh'
echo
echo "Everything except for the final READ should have failed."
echo "We can see that the worker is not granted VCAP_SERVICES, so wouldn't know"
echo "how to connect with write access."
