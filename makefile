.PHONY: install build build_release

install:
	pip install -r requirements.txt
	pip install pyinstaller

build:
	pyinstaller --onefile --console --icon "src\icons\Feather1.ico" --add-data="src/icons/Feather1.ico;icons" --name "Lexi_debug" src\app.py

build_release:
	pyinstaller --onefile --noconsole --icon "src\icons\Feather1.ico" --add-data="src/icons/Feather1.ico;icons" --name "Lexi" src\app.py