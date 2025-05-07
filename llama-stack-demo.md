# LLama Stack Demo
ssh -i ".\Downloads\DttLab_20250506.pem" azureuser@172.206.50.74
## VM Specs:


### Clave Acceso:
"C:\Users\<user>\Downloads\DttLab_key_20250503.pem"



## Preparación de Discos 

Llama 4 requiere alrededo de 300Gb de disco.

> En Linux los modelos de descargan en ./llama/checkpoints
> Si bien es posible manipular las variables de entorno para cambiar esta ruta, 
> Nosotros elegimos montar una unidad con el espacio suficiente en ./llama/

Check Disks:
sudo lsblk

Particionar Discos:
sudo fdisk /dev/sdc

Open a terminal and run sudo fdisk /dev/sdX, replacing /dev/sdX with the correct disk identifier.
Use the n command to create a new partition.
Specify the partition type (primary or logical), starting sector, and ending sector or size.
Use the w command to write the changes.

### Formatear Disco:

```
mkfs.ext4 /dev/sdc1
```

### Montar Disco:

El Servicio y sus dependencias se installan en /home/<user>/.llama/distributions/ y el modelo en /home/<user>/.llama/checkpoints

```
cd ~
mkdir llamademo
sudo chown -R azureuser ~/llamademo
sudo chmod -R 755 ~/llamademo
```

```
cd ~
mkdir .llama
sudo chown -R azureuser ~/.llama
sudo chmod -R 755 ~/.llama
```

> *Check disk UUID* (in azure disk labels may change)
>```
>blkid
>```
> Los resultados deberian ser algo asi:

>```
>SDC1 UUID="0e0bf163-8a7c-487d-999f-5b8d78385d30" BLOCK_SIZE="4096" TYPE="ext4" PARTUUID="4c07a977-01"
>```

### Montar Unidad:
```
sudo mount /dev/sdc1 ~/llamademo
```

### Ajustar fstab:

```
sudo vim /etc/fstab
```
Incuir en FSTAB:

```
>> UUID="0e0bf163-8a7c-487d-999f-5b8d78385d30"   /home/azureuser/llamademo   ext4   defaults,noatime   0   0
>> UUID="0e0bf163-8a7c-487d-999f-5b8d78385d30"   /home/azureuser/.llama   ext4   defaults,noatime,nofail   0   0

```

### Para redimencionar el disco en caso de ser necesario:


```
az disk update --resource-group ResourceGroup --name DttLab_OsDisk_1_80c7f9587ed54f6d974f70c6b294afd5 --size-gb 64
```

```
az disk update --resource-group ResourceGroup --name DttLab_llamamodel --size-gb 300
```

Verifica el tamaño del disco: Una vez que la máquina virtual esté en funcionamiento, verifica que el sistema operativo detecte el nuevo tamaño del disco. Puedes usar el siguiente comando:

Bash
```
   df -h
```
Expande la partición y el sistema de archivos: Si el sistema no expande automáticamente la partición, puedes hacerlo manualmente. Usa growpart para expandir la partición y resize2fs para expandir el sistema de archivos. Aquí tienes un ejemplo de cómo hacerlo:
Instala cloud-guest-utils si no está instalado:
Bash
```
     sudo apt-get update
     sudo apt-get install cloud-guest-utils
```

Expande la partición:
Bash
```
     sudo growpart /dev/sda 1
```
  
Expande el sistema de archivos:
Bash
```
     sudo resize2fs /dev/sda1
```

## Preparación del entorno de trabajo:
### Instalar Anaconda3

```
mkdir anacondainstall
cd anacondainstall
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
```

### Instalar anaconda
```
bash ./Anaconda3-2024.10-1-Linux-x86_64.sh
```
Salimos del terminal y volvemos a entrar para que los cambios tengan efecto.
```
exit
```

### Crear Env

Configurar carpeta de entornos en disco externo
conda config --append envs_dirs /home/azureuser/llamademo/envs

Crear entorno en carpeta especifica:
conda create --prefix /home/azureuser/llamademo/envs/llamademoenv python=3.10

Verificar envs:
conda info --envs

Ambos, el nombre del entorno y la carpeta deben ser la correcata:

```
(base) azureuser@DttLab:~$ conda info --envs
# conda environments:
#

base                  *  /home/azureuser/anaconda3
llamademoenv             /home/azureuser/llamademo/envs/llamademoenv
```

conda activate llamademoenv

### Instalar CUDA 
sudo apt install nvidia-cuda-toolkit
Check:
nvcc --version

## Installar Llama Stack



### Pre-Requisitos
Listar Modelos:
llama model list

#### Dowload the model:
Listar Modelos

> ***Ref:*** https://llama-stack.readthedocs.io/en/latest/references/llama_cli_reference/download_models.html

```
llama download --source meta --model-id Llama-4-Scout-17B-16E-Instruct --meta-url 'https://llama4.llamameta.net/*?Policy=eyJTdGF0ZW1lbnQiOlt7InVuaXF1ZV9oYXNoIjoiOTF4eDN1OGF0bWNkZmk2emlzbGdqZjRsIiwiUmVzb3VyY2UiOiJodHRwczpcL1wvbGxhbWE0LmxsYW1hbWV0YS5uZXRcLyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NDYyMTEzODV9fX1dfQ__&Signature=Suv1lPXqOmxCRyKVgznxKQfNyj3RLUZ0pH75X%7EDfBS99EjNdPpNNQQH0pzmbLR0q-7iUp7U1N03M-yxH5I7Mt-Mn6wRjjoUnEO4OyRzL1WobZU6VOoSRTRZq6mzoAmyoz6WcFVQryCUfc8yW3KQdsnu%7Eck-o0d9qyZepgvqVDeu-XxfhFjwOF6N4PXPEbqCb1f1dsGKngvK07a75Cy5kmxywuhC1TPTuHmU3xUkBdxLW50S31at9e9tyfNikPduF%7EgOLKTRkwgRucazxcP6QhDKj%7EPHbVpFfJ7XJ9AIuaKWGRh7%7EyHAgkNsDJw29UZWG0ZmQQndjniM9iYD4Cyo%7EgA__&Key-Pair-Id=K15QRJLYKIFSLZ&Download-Request-ID=1646758282642073'
```

https://llama4.llamameta.net/*?Policy=eyJTdGF0ZW1lbnQiOlt7InVuaXF1ZV9oYXNoIjoiOTF4eDN1OGF0bWNkZmk2emlzbGdqZjRsIiwiUmVzb3VyY2UiOiJodHRwczpcL1wvbGxhbWE0LmxsYW1hbWV0YS5uZXRcLyoiLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NDYyMTEzODV9fX1dfQ__&Signature=Suv1lPXqOmxCRyKVgznxKQfNyj3RLUZ0pH75X%7EDfBS99EjNdPpNNQQH0pzmbLR0q-7iUp7U1N03M-yxH5I7Mt-Mn6wRjjoUnEO4OyRzL1WobZU6VOoSRTRZq6mzoAmyoz6WcFVQryCUfc8yW3KQdsnu%7Eck-o0d9qyZepgvqVDeu-XxfhFjwOF6N4PXPEbqCb1f1dsGKngvK07a75Cy5kmxywuhC1TPTuHmU3xUkBdxLW50S31at9e9tyfNikPduF%7EgOLKTRkwgRucazxcP6QhDKj%7EPHbVpFfJ7XJ9AIuaKWGRh7%7EyHAgkNsDJw29UZWG0ZmQQndjniM9iYD4Cyo%7EgA__&Key-Pair-Id=K15QRJLYKIFSLZ&Download-Request-ID=1646758282642073



> Ref: https://hub.docker.com/r/llamastack/distribution-meta-reference-gpu


verificar que el stack se haya instalado en el disco deseado, ya que los modelos se descargan en una subcarpeta:

```
(llamademoenv) azureuser@DttLab:~$ which llama
/home/azureuser/llamademo/envs/llamademoenv/bin/llama
```


### Instalación

```
conda activate llamademoenv
pip install llama-stack
llama stack build --template meta-reference-gpu --image-type conda
```

### Ejecución del Servicio

```
cd /home/azureuser/llamademo
conda activate llamademoenv
llama stack run .llama/distributions/meta-reference-gpu/meta-reference-gpu-run.yaml \
  --port 5001 \
  --env INFERENCE_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct
```




```
llama download --source meta --model-id Llama3.2-3B-Instruct --meta-url 'https://llama3-2-lightweight.llamameta.net/*?Policy=eyJTdGF0ZW1lbnQiOlt7InVuaXF1ZV9oYXNoIjoiaWlqbGEzbDNwcjNsdWR6Y2dqM3g4OGU0IiwiUmVzb3VyY2UiOiJodHRwczpcL1wvbGxhbWEzLTItbGlnaHR3ZWlnaHQubGxhbWFtZXRhLm5ldFwvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc0NjUwMDI5Mn19fV19&Signature=HLnBQRFfWtKnZ%7En0OtR4thMq1Nl%7ElPJ1%7E2Ai-uunYkteGSxdak8goPQAK2C4JunvlP4Idokj8I4PV4FlCNsnIITNOVGrD%7EKNFP6atM%7E1Uzzt0MrL%7EzGCISdodzgW-STyQrVVK4PZy-o6a3YJJrqVaK4nV%7EjpYfC0a9wBqp-8nVeFzUnzmrN2xmNBY9SYAQR6fG6V1CzYu7pVO4S8Li-maUrvusEJnt83w7vtQLwYUvfm%7E5giQeagB7OcXFEyik0cduyYIY%7EcgCJSYTKLFSJ5Sm2Bvj1yXtyKDqQJOBgAHFFhXnrD9iYwIz4l%7E%7E-vR9w8MJ6ushqTMQ%7Ea4xp4kqDFbA__&Key-Pair-Id=K15QRJLYKIFSLZ&Download-Request-ID=1224462469328390'
```


```
cd /home/azureuser/llamademo
conda activate llamademoenv
llama stack run .llama/distributions/meta-reference-gpu/meta-reference-gpu-run.yaml \
  --port 5001 \
  --env INFERENCE_MODEL=meta-llama/Llama-3.2-3B-Instruct
```




### Some Examples

https://github.com/meta-llama/llama-stack-apps/tree/main/examples

Bash:
```
conda activate llamaapps
cd ~/Documents/llamademo/llama-stack-apps
python -m examples.agents.simple_chat --host 20.72.80.241 --port 5001

python -m examples.agents.chat_with_documents --host 20.72.80.241 --port 5001


```








# Anexos
## llama-stack-client configure

Bash:
```
(llamaapps) C:\Users\azureuser>llama-stack-client configure
> Enter the endpoint of the Llama Stack distribution server: http://20.72.80.241:5001
```


## nvidia-driver

Bash:
```
$ $ wget https://developer.download.nvidia.com/compute/nvidia-driver/$version/local_installers/nvidia-driver-local-repo-$ubuntu2404-575_x86_64_ext.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
```


# rpm --install nvidia-driver-local-repo-ubuntu2404.$version*.x86_64.rpm


