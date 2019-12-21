PROJECT_NAME = weak
INSTALL_PATH = $(HOME)/bin/$(PROJECT_NAME)
GEN_PYC_EXE = ./frw/gen_pyc.py
BUILD_PATH = ./vbuild

.PHONY: build install clean

build:
	@echo "build..."
	@python $(GEN_PYC_EXE) ./ -e $(BUILD_PATH) -f

	@cp -r ./gui/conf $(BUILD_PATH)/gui/conf
	@cp -r ./gui/res  $(BUILD_PATH)/gui/res
	@cp -r ./gui/ui   $(BUILD_PATH)/gui/ui

	@rm -rf $(BUILD_PATH)/thinking/
	@rm $(BUILD_PATH)/frw/gen_pyc.pyc

compile:
	@echo "compile..."
	@python $(GEN_PYC_EXE) ./ -f

install: build
	@echo "install..."
	@test ! -d $(INSTALL_PATH) || rm -rf $(INSTALL_PATH)
	@mv -f $(BUILD_PATH) $(INSTALL_PATH)

clean:
	@test ! -d $(BUILD_PATH) || rm -rf $(BUILD_PATH)
	@#find ./ -type d -name __pycache__ -exec rm -r {} \;  # -exec rm 报错，终止make
	@find ./ -type d -name __pycache__ | xargs rm -rf
	@#find ./ -name "*.pyc" | xargs rm
