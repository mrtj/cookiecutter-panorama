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

BUILD_DIR := build


# --------- External variables ---------

PROJECT_SLUG := {{ cookiecutter.project_slug }}
MODEL_PACKAGE_NAME := {{ cookiecutter.model_package_name }}
MODEL_PACKAGE_VERSION := {{ cookiecutter.model_package_version }}
MODEL_ASSET_NAME := {{ cookiecutter.model_asset_name }}
CODE_PACKAGE_NAME := {{ cookiecutter.code_package_name }}
S3_WORKING_PATH := {{ cookiecutter.s3_working_path }}


# --------- Targets to create dummy pytorch model ---------

MODEL_SCRIPT_FILE := $(BUILD_DIR)/create_model.py
MODEL_FILE := $(BUILD_DIR)/$(MODEL_PACKAGE_NAME).pth
MODEL_ARCHIVE_BASENAME := models/$(MODEL_PACKAGE_NAME)
MODEL_ARCHIVE := $(MODEL_ARCHIVE_BASENAME).tar.gz

define MODEL_SOURCE
import sys, torch

class MeanNet(torch.nn.Module):
    def forward(self, x):
        return torch.mean(x, dim=(2, 3))

torch.jit.script(MeanNet()).save(sys.argv[1])
endef
export MODEL_SOURCE

$(MODEL_SCRIPT_FILE): | build_dir
	@echo "$$MODEL_SOURCE" > $(MODEL_SCRIPT_FILE)

$(MODEL_FILE): $(MODEL_SCRIPT_FILE)
	@python $(MODEL_SCRIPT_FILE) $(MODEL_FILE)

$(MODEL_ARCHIVE): $(MODEL_FILE)
	@tar -C $(BUILD_DIR) -czf $(MODEL_ARCHIVE) $(MODEL_PACKAGE_NAME).pth


# --------- Targets to get the AWS account id used in this project ---------

ACCOUNT_ID_SCRIPT_FILE := $(BUILD_DIR)/account_id.py

define ACCOUNT_ID_SOURCE
import json, os
slug = '$(PROJECT_SLUG)'
package_name = '$(CODE_PACKAGE_NAME)'
with open(os.path.join(slug, 'graphs', slug, 'graph.json')) as f:
    graph = json.load(f)
for package in graph['nodeGraph']['packages']:
    if package['name'].endswith(package_name):
	    print(package['name'].split('::')[0])
endef
export ACCOUNT_ID_SOURCE

$(ACCOUNT_ID_SCRIPT_FILE): build_dir
	@echo "$$ACCOUNT_ID_SOURCE" > $(ACCOUNT_ID_SCRIPT_FILE)

set_account_id: $(ACCOUNT_ID_SCRIPT_FILE)
	$(eval AWS_ACCOUNT_ID := $(shell python $(ACCOUNT_ID_SCRIPT_FILE)))


# --------- Targets to set up AWS test utility ---------

TEST_UTILITY_URL := https://github.com/mrtj/aws-panorama-test-utility.git
TEST_UTILITY_PATH := $(BUILD_DIR)/aws-panorama-test-utility
TEST_UTILITY_ENTRY_POINT := ${TEST_UTILITY_PATH}/test_utility/panorama_test_utility_run.py
TEST_UTILITY_COMPILE_ENTRY_POINT := ${TEST_UTILITY_PATH}/test_utility/panorama_test_utility_compile.py
TEST_UTILITY_MODEL := models/$(MODEL_ASSET_NAME)

define MODEL_INFO_SCRIPT
import sys,json; info=json.load(sys.stdin)['mlModelDescriptor']
endef
export MODEL_INFO_SCRIPT

$(TEST_UTILITY_PATH): | build_dir
	git clone $(TEST_UTILITY_URL) $(TEST_UTILITY_PATH)

set_model_info: set_account_id
	$(eval MODEL_PACKAGE_PATH := $(PROJECT_SLUG)/packages/${AWS_ACCOUNT_ID}-${MODEL_PACKAGE_NAME}-${MODEL_PACKAGE_VERSION})
	$(eval MODEL_FRAMEWORK :=  $(shell cat ${MODEL_PACKAGE_PATH}/descriptor.json | python -c "$(MODEL_INFO_SCRIPT); print(info['framework'])"))
	$(eval MODEL_INPUT_SHAPE := $(shell cat ${MODEL_PACKAGE_PATH}/descriptor.json | python -c "$(MODEL_INFO_SCRIPT); print(info['inputs'][0]['shape'])"))
	$(eval MODEL_INPUT_NAME :=  $(shell cat ${MODEL_PACKAGE_PATH}/descriptor.json | python -c "$(MODEL_INFO_SCRIPT); print(info['inputs'][0]['name'])"))

$(TEST_UTILITY_MODEL): | $(TEST_UTILITY_PATH) set_model_info
	@echo Compiling model $(MODEL_ARCHIVE) for test utility ...
	python $(TEST_UTILITY_COMPILE_ENTRY_POINT) \
		--s3-model-location $(S3_WORKING_PATH) \
		--model-node-name $(MODEL_ASSET_NAME) \
		--model-file-basename $(MODEL_ARCHIVE_BASENAME) \
		--model-data-shape "{\"$(MODEL_INPUT_NAME)\":$(MODEL_INPUT_SHAPE)}" \
		--model-framework '$(MODEL_FRAMEWORK)'

# --------- Build project ---------

build_model: | $(MODEL_ARCHIVE)	set_account_id			## Builds the model into the Panorama project
	$(eval MODEL_PACKAGE_PATH := ./packages/${AWS_ACCOUNT_ID}-${MODEL_PACKAGE_NAME}-${MODEL_PACKAGE_VERSION})
	cd $(PROJECT_SLUG) && \
	panorama-cli add-raw-model \
		--model-asset-name $(MODEL_ASSET_NAME) \
		--model-local-path ../$(MODEL_ARCHIVE) \
		--descriptor-path $(MODEL_PACKAGE_PATH)/descriptor.json \
		--packages-path $(MODEL_PACKAGE_PATH)

# --------- Global targets ---------

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

build_dir:
	@mkdir -p $(BUILD_DIR)

raw_model: | $(MODEL_ARCHIVE) 							## Creates a dummy pytorch model

test_utility: | $(TEST_UTILITY_PATH)					## Installs AWS Panorama Test Utility

test_utility_model: | $(TEST_UTILITY_MODEL)				## Compiles the model for Test Utility



build: build_dir raw_model set_account_id			 	## Builds the Panorama project
	@echo "Build"
	echo $(AWS_ACCOUNT_ID)

clean:								## Cleans the build artifacts
	@rm -rf build
