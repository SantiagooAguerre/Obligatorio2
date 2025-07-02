#! /bin/bash
clear
echo "* * *                      * * *"
echo "*   BIENVENIDO A LOS BACKUPS   *"
echo "* * *                      * * *"
usuario="100"
while [ $usuario -ne 0 ]
do
	echo ""
	echo "//////////////////////////////////////"
	echo "/// 1- Crear Backup con parámetros ///"
	echo "//////////////////////////////////////"
	echo ""
	echo ""
	echo "////////////////////////////////////////////////////"
	echo "/// 2- Más opciones para los archivos del Backup ///"
	echo "////////////////////////////////////////////////////"
	echo ""
	echo ""
	echo "////////////////"
	echo "/// 0- Salir ///"
	echo "////////////////"
	echo ""
	read usuario
	case $usuario in
		1) sh scripts/parametros.sh;;
		2) sh scripts/configuraciones.sh;;
		0) clear
		echo "<-------- SALIENDO... <--------"
		echo;;
		*) echo "La opcion es incorrecta";;
	esac
done
