set -e
docker build -t noid-generation .

docker run -it --rm --name noid-gen-run \
   -v "${PWD}":/home/jovyan/work \
   -w /home/jovyan/work \
   noid-generation "$@"
