.PHONY: help build clean #package
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

define MODEL_SOURCE
import sys, torch

class MeanNet(torch.nn.Module):
    def forward(self, x):
        return torch.mean(x, dim=(2, 3))

torch.jit.script(MeanNet()).save(sys.argv[1])
endef
export MODEL_SOURCE

BUILD_DIR := build
MODEL_SCRIPT_FILE := $(BUILD_DIR)/create_model.py
MODEL_BASENAME := {{cookiecutter.model_package_name}}
MODEL_FILE := $(BUILD_DIR)/$(MODEL_BASENAME).pth
MODEL_ARCHIVE := models/$(MODEL_BASENAME).tar.gz

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

build_dir:
	@mkdir -p $(BUILD_DIR)

$(MODEL_SCRIPT_FILE): build_dir
	@echo "$$MODEL_SOURCE" > $(MODEL_SCRIPT_FILE)

$(MODEL_FILE): $(MODEL_SCRIPT_FILE)
	@python $(MODEL_SCRIPT_FILE) $(MODEL_FILE)

$(MODEL_ARCHIVE): $(MODEL_FILE)
	@tar -C $(BUILD_DIR) -czf $(MODEL_ARCHIVE) $(MODEL_BASENAME).pth

raw_model: | $(MODEL_ARCHIVE) 			## Creates a dummy pytorch model

build: build_dir raw_model					## Builds the Panorama project
	@echo "Build"

clean:								## Cleans the build artifacts
	@rm -rf build
