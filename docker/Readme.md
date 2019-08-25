You can try on rujaion docker image as follows.

Allow the local machine to connect to X windows display.
```bash
echo "xhost local:" >> ~/.bashrc
source ~/.bashrc
```

Build Image.
```bash
docker build -t rujaion/rujaion .
```
Run Image.
```bash
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix/:/tmp/.X11-unix rujaion/rujaion /bin/bash
```

Execute rujaion
```bash
rujaion_main.py
```
