.PHONY: help build clean #package
.DEFAULT_GOAL := help

BUILD_DIR := _build
SCRIPTS_DIR := scripts

# --------- External variables ---------

PROJECT_SLUG := {{ cookiecutter.project_slug }}

CODE_PACKAGE_NAME := {{ cookiecutter.code_package_name }}
CODE_PACKAGE_VERSION := {{ cookiecutter.code_package_version }}
CODE_ASSET_NAME := {{ cookiecutter.code_asset_name }}

MODEL_PACKAGE_NAME := {{ cookiecutter.model_package_name }}
MODEL_PACKAGE_VERSION := {{ cookiecutter.model_package_version }}
MODEL_ASSET_NAME := {{ cookiecutter.model_asset_name }}

S3_WORKING_PATH := {{ cookiecutter.s3_working_path }}

# --------- Derived variables ---------

AWS_ACCOUNT_ID_SCRIPT := $(SCRIPTS_DIR)/account_id.py
AWS_ACCOUNT_ID := $(shell python $(AWS_ACCOUNT_ID_SCRIPT))

CODE_INFO_SCRIPT := import sys,json; info=json.load(sys.stdin)['runtimeDescriptor']
MODEL_INFO_SCRIPT := import sys,json; info=json.load(sys.stdin)['mlModelDescriptor']

CODE_PACKAGE_PATH := packages/$(AWS_ACCOUNT_ID)-$(CODE_PACKAGE_NAME)-$(CODE_PACKAGE_VERSION)
CODE_PACKAGE_PATH_BUILD := $(PROJECT_SLUG)/$(CODE_PACKAGE_PATH)
CODE_DESCRIPTOR_PATH := $(CODE_PACKAGE_PATH_BUILD)/descriptor.json
CODE_ENTRY_POINT := $(shell cat $(CODE_DESCRIPTOR_PATH) | python -c "$(CODE_INFO_SCRIPT); print(info['entry']['name'].replace('/panorama', '/src'))")
CODE_SOURCES := $(wildcard $(CODE_PACKAGE_PATH_BUILD)/**/*)

MODEL_PACKAGE_PATH := packages/$(AWS_ACCOUNT_ID)-$(MODEL_PACKAGE_NAME)-$(MODEL_PACKAGE_VERSION)
MODEL_PACKAGE_PATH_BUILD := $(PROJECT_SLUG)/$(MODEL_PACKAGE_PATH)
MODEL_DESCRIPTOR_PATH := $(MODEL_PACKAGE_PATH_BUILD)/descriptor.json
MODEL_FRAMEWORK :=  $(shell cat $(MODEL_DESCRIPTOR_PATH) | python -c "$(MODEL_INFO_SCRIPT); print(info['framework'])")
MODEL_INPUT_SHAPE := $(shell cat $(MODEL_DESCRIPTOR_PATH) | python -c "$(MODEL_INFO_SCRIPT); print(info['inputs'][0]['shape'])")
MODEL_INPUT_NAME :=  $(shell cat $(MODEL_DESCRIPTOR_PATH) | python -c "$(MODEL_INFO_SCRIPT); print(info['inputs'][0]['name'])")
MODEL_SOURCES := $(wildcard $(MODEL_PACKAGE_PATH_BUILD)/**/*)

MODEL_ARCHIVE_BASENAME := models/$(MODEL_PACKAGE_NAME)
MODEL_ARCHIVE := $(MODEL_ARCHIVE_BASENAME).tar.gz

# --------- Help script ---------

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

# --------- Targets to create dummy pytorch model ---------

DUMMY_MODEL_SCRIPT := $(SCRIPTS_DIR)/create_model.py
DUMMY_MODEL_FILE := $(BUILD_DIR)/$(MODEL_PACKAGE_NAME).pth

$(DUMMY_MODEL_FILE): | $(DUMMY_MODEL_SCRIPT) $(BUILD_DIR)
	@echo INFO: Creating dummy pytorch model ...
	@python $(DUMMY_MODEL_SCRIPT) $(DUMMY_MODEL_FILE)

$(MODEL_ARCHIVE): | $(DUMMY_MODEL_FILE)
	@echo INFO: No raw model was found at $(MODEL_ARCHIVE). Creating a dummy model.
	@tar -C $(BUILD_DIR) -czf $(MODEL_ARCHIVE) $(MODEL_PACKAGE_NAME).pth
	@echo INFO: Dummy model asset was created at $(MODEL_ARCHIVE).
	@echo INFO: Replace this file with your real model.

# --------- Targets to set up AWS test utility ---------

TEST_UTILITY_URL := https://github.com/mrtj/aws-panorama-test-utility.git
TEST_UTILITY_PATH := $(BUILD_DIR)/aws-panorama-test-utility
TEST_UTILITY_ENTRY_POINT := ${TEST_UTILITY_PATH}/test_utility/panorama_test_utility_run.py
TEST_UTILITY_COMPILE_ENTRY_POINT := ${TEST_UTILITY_PATH}/test_utility/panorama_test_utility_compile.py
TEST_UTILITY_MODEL := models/$(MODEL_ASSET_NAME)
TEST_UTILITY_OUTPUT_DIR := ./test_output

VIDEO_START ?= 0
VIDEO_STEP ?= 1
VIDEO_STOP ?= 1000000
NO_VIDEO_ERROR_MSG := \nUsage: make test_utility VIDEO_FILE=sample.mp4 [VIDEO_START=123] [VIDEO_STOP=234] [VIDEO_STEP=2]\nERROR: VIDEO_FILE is not defined.\n

$(TEST_UTILITY_PATH): | $(BUILD_DIR)
	@echo
	@echo INFO: Installing Panorama Test Utility ...
	@echo
	git clone $(TEST_UTILITY_URL) $(TEST_UTILITY_PATH)

$(TEST_UTILITY_MODEL): $(MODEL_ARCHIVE) | $(TEST_UTILITY_PATH)
	@echo
	@echo INFO: Compiling $(MODEL_ARCHIVE) for test utility ...
	@echo
	@python $(TEST_UTILITY_COMPILE_ENTRY_POINT) \
		--s3-model-location $(S3_WORKING_PATH) \
		--model-node-name $(MODEL_ASSET_NAME) \
		--model-file-basename $(MODEL_ARCHIVE_BASENAME) \
		--model-data-shape "{\"$(MODEL_INPUT_NAME)\":$(MODEL_INPUT_SHAPE)}" \
		--model-framework '$(MODEL_FRAMEWORK)'

$(TEST_UTILITY_OUTPUT_DIR):
	@mkdir -p $(TEST_UTILITY_OUTPUT_DIR)

do_run_test_utility: | $(TEST_UTILITY_MODEL) $(TEST_UTILITY_OUTPUT_DIR)
	@echo
	@echo INFO: Starting Panorama Test Utility ...
	@echo
	@test -n "$(VIDEO_FILE)" || (echo "$(NO_VIDEO_ERROR_MSG)"; exit 1)
	@rm -f $(TEST_UTILITY_OUTPUT_DIR)/*
	@TEST_UTILITY_ENVIRONMENT=1 python $(TEST_UTILITY_ENTRY_POINT) \
		--app-name $(PROJECT_SLUG) \
		--code-package-name $(CODE_PACKAGE_NAME) \
		--py-file $(PROJECT_SLUG)/$(CODE_PACKAGE_PATH)$(CODE_ENTRY_POINT) \
		--video-file $(VIDEO_FILE) \
		--model-file-basename $(MODEL_ARCHIVE_BASENAME) \
		--model-node-name $(MODEL_ASSET_NAME) \
		--output-screenshots $(TEST_UTILITY_OUTPUT_DIR) \
		--video-start $(VIDEO_START) \
		--video-step $(VIDEO_STEP) \
		--video-stop $(VIDEO_STOP)

# --------- Build project ---------

BUILD_MODEL_FLAG := $(BUILD_DIR)/build_model

build_model: $(BUILD_MODEL_FLAG) ## Builds the model into the Panorama project

$(BUILD_MODEL_FLAG): $(MODEL_SOURCES) $(MODEL_ARCHIVE) | $(BUILD_DIR)
	@echo
	@echo INFO: Building model ...
	@echo
	cd $(PROJECT_SLUG) && \
	panorama-cli add-raw-model \
		--model-asset-name $(MODEL_ASSET_NAME) \
		--model-local-path ../$(MODEL_ARCHIVE) \
		--descriptor-path $(MODEL_PACKAGE_PATH)/descriptor.json \
		--packages-path $(MODEL_PACKAGE_PATH)
	@touch $(BUILD_MODEL_FLAG)

BUILD_CODE_FLAG := $(BUILD_DIR)/build_code

build_code: $(BUILD_CODE_FLAG)

$(BUILD_CODE_FLAG): $(CODE_SOURCES) | $(BUILD_DIR)
	@echo
	@echo INFO: Building code container ...
	@echo
	cd $(PROJECT_SLUG) && \
	panorama-cli build-container \
		--container-asset-name $(CODE_ASSET_NAME) \
		--package-path $(CODE_PACKAGE_PATH)
	@touch $(BUILD_CODE_FLAG)

# --------- Global targets ---------

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

build: build_model build_code			 				## Builds the Panorama project

dummy_model: | $(MODEL_ARCHIVE) 						## Creates a dummy pytorch model

install_test_utility: | $(TEST_UTILITY_PATH)			## Installs AWS Panorama Test Utility

test_utility_model: | $(TEST_UTILITY_MODEL)				## Compiles the model for Test Utility

test_utility: do_run_test_utility						## Runs the Test Utility

clean:													## Cleans the build artifacts
	@rm -rf $(BUILD_DIR)
