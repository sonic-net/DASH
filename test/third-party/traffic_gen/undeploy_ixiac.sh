dir_path="$( dirname ${BASH_SOURCE[0]:-$0})"
echo $dir_path
cd $dir_path
docker-compose -f deployment/ixia-c-deployment.yml down 
