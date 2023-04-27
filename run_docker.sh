set -e
docker build -t rdhyee/noid-generation .
PORT=${1:-8888}


docker run \
   -v "${PWD}":/home/jovyan/work \
   -p $PORT:8888 \
   -e GEN_CERT=yes \
   -e GRANT_SUDO=yes \
   rdhyee/noid-generation \
   start-notebook.sh \
   --NotebookApp.password='argon2:$argon2id$v=19$m=10240,t=10,p=8$qvckJKX8B1thQjA0CYmw/Q$v8nHdCbdSZPfxWCVU7bIhI0w4/GjWZuNsrw8AkhWXdo'
