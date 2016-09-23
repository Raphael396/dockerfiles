#!/bin/sh

op=$1
shift
IMAGE="calebj/red-discordbot:data"

case $op in
    "backup")
    if [ ! -e ${1}.tar ]; then
        docker run --rm --volumes-from $1 -v $(pwd):/backup $IMAGE \
            tar cvf /backup/$1.tar -C /data/ .
        ec=$?
        [ $ec == 0 ] || exit $ec
        echo "Backup complete."
    else
        echo "ERROR: ${1}.tar already exists in cwd; not overwriting."
        exit 1
    fi
    ;;
    "create")
    docker run --name $1 $IMAGE true
    ec=$?
    [ $ec == 0 ] || exit $ec
    echo "Data container created."
    ;;
    "restore")
    if [ -e ${1}.tar ]; then
        docker run --name $1 $IMAGE true
        ec=$?
        [ $ec == 0 ] || exit $ec
        docker run --rm --volumes-from $1 -v $(pwd):/backup $IMAGE \
            tar xvf /backup/$1.tar -C /data/ .
        echo "New data container restored from archive."
    else
        echo "ERROR: ${1}.tar doesn't exist."
        exit 1
    fi;;
    "reset")
    docker run --rm --volumes-from $1 $IMAGE reset_core_data
    ec=$?
    [ $ec == 0 ] || exit $ec
    echo "Core cogs and data reset to repo contents."
    echo "Any custom files have been renamed."
    ;;
esac
