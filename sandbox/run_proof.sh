echo "Testing read/write configuration between workers and DB."
echo
echo "The worker will check to see if it can import dev and prod dependencies."
echo "We expect it to import production, but not development dependencies"
echo ""
echo "Here's that, but in a diagram:"
echo ""
echo "+------------+           +---------+"
echo "|  Worker 1  |   import  | Python  |"
echo "|   (./app)  |<--------->| (./deps)|"
echo "+------------+           +---------+"
echo ""
read -p "...Press enter to start the test..."
echo ""
echo "Checking database access for worker1:"
cf ssh "crt-portal-sandbox-worker1-$(whoami)" -c './app/run_proof_remote.sh'
echo
