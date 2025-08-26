# Desde la raiz del repo correr:
python -m src.runner

# o Podria tambien ser
python3 -m src.runner

# Si estan en MacOS puede faltar la instalacion de tkinter
# En ese caso, correr:
brew install python-tk

# Si estan en linux y falta tkinter:
sudo apt update
sudo apt install python3-tk


# Para ver la animacion simultanea de los diferentes metodos de busqueda
python -m src.animation_all_results src/results/level_6_results.csv level_6 src/maps/level_6.txt

# Para guardar soluciones de otro nivel
python -m src.level_results level_1