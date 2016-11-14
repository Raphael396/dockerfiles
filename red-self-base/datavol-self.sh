#!/bin/bash

op=$1
shift
IMAGE="calebj/red-selfbot:data"

function usage {
    echo "Usage:
    datavol create RED_NAME
    datavol import RED_NAME RED_PATH
    datavol backup RED_NAME [TARFILE]
    datavol restore RED_NAME [TARFILE]
    datavol reset RED_NAME
    
    RED_NAME should be some identifier for your bot, usually its name."
}

if [ x"$1" == x -o x"$op" == x ]; then
    usage
    exit
fi

NAME=$1
CONTAINER=red-$NAME-data
shift

case $op in
    "backup")
    TARNAME=${1:-${NAME}.tar}
    if [ ! -e $TARNAME ]; then
        docker run --rm --volumes-from $CONTAINER -v $(pwd):/backup $IMAGE \
            tar cf /backup/$TARNAME -C /data/ .
        echo "Backup saved to $TARNAME."
    else
        echo "ERROR: $TARNAME already exists in cwd; not overwriting."
        exit 1
    fi
    ;;

    "create")
    docker run --name $CONTAINER $IMAGE true || exit $?
    echo "Data container $CONTAINER created."
    ;;

    "restore")
    TARNAME=${1:-${NAME}.tar}
    if [ -e $TARNAME ]; then
        docker run --name $CONTAINER $IMAGE true || exit $?
        docker run --rm --volumes-from $CONTAINER -v $(pwd):/backup $IMAGE \
            tar xf /backup/$TARNAME -C /data/ . || exit $?
        echo "Data container $CONTAINER restored from archive."
    else
        echo "ERROR: $TARNAME doesn't exist."
        exit 1
    fi
    ;;

    "reset")
    docker run --rm --volumes-from $CONTAINER $IMAGE reset_core_data
    ec=$?
    [ $ec == 0 ] || exit $ec
    echo "Core cogs and data reset to repo contents."
    echo "Any custom files have been renamed."
    ;;

    "import")
    if [ x"$1" == x ]; then
        echo "ERROR: You must specify a folder to import"
        usage
        exit 1
    fi
    if [ -d ${1}/data -a -d ${1}/cogs ]; then
        docker run --name $CONTAINER $IMAGE true || exit $?
        docker run --rm --volumes-from $CONTAINER -v "$(pwd)/${1}":/import --user red $IMAGE \
            cp -r --remove-destination /import/cogs /import/data /data/red/
        echo -e "Red installation imported to $CONTAINER.\nIt is strongly recommended that you do datavol reset $NAME to re-link the stock cogs."
    else
        echo "ERROR: ${1} doesn't look like a Red installation."
        usage
        exit 1
    fi
    ;;
    *)
    echo "Unknown operation $op"
    usage
    exit 1
    ;;
esac
