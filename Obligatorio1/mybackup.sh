#!/bin/bash

directorio="$(cd "$(dirname "$0")" && pwd)"
cd "$directorio"

case "$1" in
	-a)	./main.sh;;

	-e)	nano mybackup.conf;;

	-b)	crontab -e;;

    	-c)
        	if [ "$2" != "-q" ]; then
            		echo "Los parámetros son incorrectos. Revise el manual de mybackup."
            		exit 1
        	fi
        	Base="$3"
        	DondeGuardar=$(grep "UBICACION_BACKUPS:" mybackup.conf | cut -d':' -f2)

        	if [ ! -e "$Base" ]; then
            		echo "El archivo o directorio especificado no existe."
			exit 1
        	fi

        	if [ ! -d "$DondeGuardar" ]; then
            		echo "El directorio especificado no existe."
            		exit 1
        	fi

        	fecha=$(date +%Y%m%d_%H%M%S)
        	nombre_base=$(basename "$Base")
        	ArchivoTar="$DondeGuardar/${nombre_base}_${fecha}.tar"
		verbose=$(grep "VERBOSE:" mybackup.conf | cut -d':' -f2)
		verificar_crontab=$(grep "MANDAR_A_CRONTAB:" mybackup.conf | cut -d':' -f2)
		tiempo=$(grep "TIEMPO:" mybackup.conf | cut -d':' -f2)
		ruta=$(pwd)"/mybackup.sh"

		if [ "$verificar_crontab" = "true" ]; then
			(crontab -l ; echo "$tiempo sh $ruta $1 $2 $3") | crontab -
		fi

		if [ "$verbose" = "true" ]; then
			tar -cvf "$ArchivoTar" -C "$(dirname "$Base")" "$nombre_base"
        	else
			tar -cf "$ArchivoTar" -C "$(dirname "$Base")" "$nombre_base"
		fi
        	gzip $ArchivoTar
		chmod 777 $ArchivoTar.gz
        	echo "El Backup quedó guardado en la ruta ${ArchivoTar}.gz."
		;;
	-d)
        	Archivo="$2"

        	if [ ! -f "$Archivo" ]; then
            		echo "El archivo especificado no existe."
            		exit 1
        	fi

		if [ "$verbose" = "true" ]; then
                       	tar -xvzf $Archivo
                else
                        tar -xzf $Archivo
                fi

        	echo "El archivo fue descomprimido y extraído correctamente."
        	;;

    	-m)
        	Archivo="$2"

        	if [ ! -f "$Archivo" ]; then
            		echo "El archivo especificado no existe."
            		exit 1
        	fi
        	tar -tzf $Archivo
        	;;

    	*)
        	echo "El parámetro especificado no existe. Revise el manual de mybackup."
        	exit 1
		;;
esac
