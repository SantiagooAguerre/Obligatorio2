#! /bin/bash
clear
usuar="100"
while [ $usuar -ne 0 ]
do
	echo ""
	echo "----------------------------------"
	echo "---- 1- Descomprimir archivo  ----"
	echo "----------------------------------"
	echo ""
	echo "--------------------------------------"
	echo "---- 2- Agregar archivos a un tar ----"
	echo "--------------------------------------"
	echo ""
	echo "----------------------------------------------------"
	echo "---- 3- Ver archivos de una carpeta comprimida  ----"
	echo "----------------------------------------------------"
	echo ""
	echo "------------------------------------------"
	echo "---- 4- Actualizar archivo comprimido ----"
	echo "------------------------------------------"
	echo ""
	echo "------------------"
	echo "---- 0- Salir ----"
	echo "------------------"
	echo ""
	read usuar
	case $usuar in
		1) while [ $desco -ne 1 ] && [ $desco -ne 2 ] && [ $desco -ne 3 ];
		do
			echo "¿Qué tipo de archivo quiere descomprimir? (1. tar, 2. gzip, 3. bzip2)"
			read desco
			case $desco in
				1) echo "¿Qué archivo quiere descomprimir? "
				read archivo
				tar -xvf $archivo
				echo "Archivo descomprimido.";;
				2) echo "¿Qué archivo quiere descomprimir? "
				read archivo
				tar -xvzf $archivo
				echo "Archivo descomprimido.";;
				3) echo "¿Qué archivo quiere descomprimir? "
				read archivo
				tar -xvjf $archivo
				echo "Archivo descomprimido.";;
				*) echo "Opción inválida.";;
			esac
		done
		usuar="0";;
		2) echo "¿Que quiere agregar al archivo tar?"
		read agregar
		echo "¿A qué archivo desea agregarlo?"
		read archivo
		tar -rvf $archivo $agregar
		echo "$agregar ha sido agregado exitosamente."
		usuar="0";;
		3) echo "¿Qué archivo comprimido quiere listar?"
		read archivo
		tar -tvf $archivo
		usuar="0";;
		4) echo "¿Qué archivo comprimido tar quiere actualizar?"
		read archivo
		echo "¿Qué quiere actualizar en el archivo?"
		read actualizacion
		tar -uvf $archivo $actualizacion
		echo "El archivo ha sido actualizado exitosamente."
		usuar="0";;
		0) echo ""
		echo "<------- Saliendo... <-------";;
		*) echo "El $usuar es incorrecto.";;
	esac
done
usuario="100"
