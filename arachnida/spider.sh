#!/bin/bash

#web="https://www.malagahoy.es"
#web="https://cadizgusta.blogspot.com/2016/05/fruteria-verduleria-paco-vazquez-conil.html"
mypath="./data"
mylinks="./links"
lnk_file="linkis.txt"
img_tmp="imgtmp.txt"
img_tmp2="imgtmp2.txt"
img_tmp3="imgtmp3.txt"
img_file="images.txt"
level=1
depth=5

while getopts r:l:p: FLAG
do
	case "${FLAG}" in
		r)
			web=${OPTARG};;
		l)

			depth=${OPTARG};;
		p)

			mypath=${OPTARG};;
	esac
done
if [[ $web != https* ]]
then
	echo "$web"
	echo "Formato incorrecto"
	echo "El programa debe usarse: ./spider -r URL (-l <nº de profundidad>) (-p <nombre de la carpeta de salida>)"
	echo "El formato de la URL debe ser: http[s]://domain"
	exit 0;
fi
	
echo -e "\033c"
echo "		La web que vamos a arañar es:"
echo "                    $web"
echo "		Las imagenes se guardaran en: $mypath"
echo "		El nivel de profundidad es: $depth"
echo 
echo "----------------------- Si es correcto, pulsa un tecla -----------------------"

read -n 1 -s -p "------------------------- Pulsa CTRL+C para cancelar -------------------------"
echo
echo "Comenzamos:"

# preparando entorno
rm -rf $mypath
rm -rf $mylinks
mkdir $mypath
mkdir $mylinks
touch $mylinks/$img_file

# Buscando los enlaces
echo
echo "Copiando enlaces..."
echo $web > "$mylinks/$lnk_file"
echo "Para nivel de profundidad $level:$(cat "$mylinks/$lnk_file" | wc -l) enlaces copiados:"
echo

while [[ $level -lt $depth ]]
do
	for line in $(cat "$mylinks/$lnk_file")
	do 
		curl -sSl $line | grep -v '.js"' | grep -Eo "https?://\S+?\"" | sed 's/.$//'| grep -v "*...$" 2>/dev/null > tmp.txt
	done
	cat tmp.txt | sort -u >> "$mylinks/$lnk_file"
	rm -rf tmp.txt
	((level++))
	echo "Para nivel de profundidad $level:$(cat "$mylinks/$lnk_file" | wc -l) enlaces copiados:"
	echo
done

# Buscando enlaces de imagenes
echo
echo "Buscando enlaces de imagenes en los enlaces descargados..."

for line in $(cat "$mylinks/$lnk_file")
do	
	echo "$line"
	rm -rf $mylinks/$img_tmp
	rm -rf $mylinks/$img_tmp2
	curl -sSL  $line | grep ".jpg\|.jpeg\|.png\|.gif\|.bmp" > $mylinks/$img_tmp
	for line2 in $(cat "$mylinks/$img_tmp")
		do
			echo "$line2" | awk -F 'href="' '{print $2}' | grep ".jpg\|.jpeg\|.png\|.gif\|.bmp" | awk -F '"' '{print $1}' | awk -F '?' '{print $1}' >> $mylinks/$img_tmp2
			echo "$line2" | grep ".jpg\|.jpeg\|.png\|.gif\|.bmp" | awk -F 'src=' '{print $2}' | cut -d "'" -f2 | cut -d '"' -f2 >> $mylinks/$img_tmp2
			echo "$line2" | awk -F 'https:' '{print $2}' | grep ".jpg\|.jpeg\|.png\|.gif\|.bmp" | cut -d "'" -f1 | cut -d '"' -f2 | cut -d ')' -f2 >> $mylinks/$img_tmp2
		done
		if [[ $(cat $mylinks/$img_tmp2 | wc -l) -gt 0 ]]
			then
				cat $mylinks/$img_tmp2 | sort -u > $mylinks/$img_tmp3
				cat $mylinks/$img_tmp3 > $mylinks/$img_tmp2
				rm -rf $mylinks/$img_tmp3
			else
				echo "No hay imagenes en este enlace"
			fi
		for tmpimg in $(cat "$mylinks/$img_tmp2")
		do
			if [[ $tmpimg == //* ]]
				then
					echo "https:$tmpimg" >> $mylinks/$img_file
				elif [[ $tmpimg == /* ]]
				then
					echo "$line$tmpimg" >> $mylinks/$img_file
				elif [[ $tmpimg == http* ]]
				then
					echo "$tmpimg" >> $mylinks/$img_file
				fi
		done
		cat $mylinks/$img_file | sort -u > $mylinks/$img_tmp
		cat $mylinks/$img_tmp > $mylinks/$img_file
		rm -rf $mylinks/$img_tmp
		rm -rf $mylinks/$img_tmp2
done

# Descargando imagenes 
echo
echo "Descargando en $mypath: $(cat "$mylinks/$img_file" | wc -l) imagenes "
for line in $(cat "$mylinks/$img_file")
do
	cd $mypath
	curl -OsL $line
	cd ..
done

# Gestionar salida
echo
echo "BOOM! Trabajo hecho. Hasta luego amigues..."
rm -rf $mylinks
exit 0;