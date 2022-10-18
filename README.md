# cookiecutter-panorama

[Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for [AWS Panorama](https://aws.amazon.com/panorama/) projects.

- GitHub repo: https://github.com/mrtj/cookiecutter-panorama/
- Free software: MIT license

## Features

- Easy-to-use Makefile based build system with rich features
- [Test Utility](https://github.com/aws-samples/aws-panorama-samples) integrated
- Git hooks to prevent leaking your AWS account identifier
- Batteries included: if you do not have a ready deep learning model, a dummy pytorch model is created for you so you can build and deploy the whole application right away.

## Quick start

Install the latest Cookiecutter if you haven't installed it yet (this requires Cookiecutter 1.4.0 or higher):

```bash
pip install -U cookiecutter
```

Generate a Panorama application project:

```bash
cookiecutter https://github.com/mrtj/cookiecutter-panorama.git
```

Then:

- Initialize a git repository in your new project with `make init-repo`.
- Install the required build tools: [aws-cli](https://aws.amazon.com/cli/), [panorama-cli](https://github.com/aws/aws-panorama-cli) and [docker](https://docs.docker.com/get-docker/). [Configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) the aws-cli to the credentials of the account where the Panorama appliance is registered.
- Import the project to your AWS account with `make import`
- Build the project with `make build`. This will also create a dummy deep learning model that you can replace later with a real model. The dummy model will simply calculate the mean of the RGB channels of the input video frame.
- Upload the compiled application container and packaged deep learning model with `make package`. This script will also output the path of the compile manifest json.
- Pick up the manifest json, head to [AWS Panorama Console](https://console.aws.amazon.com/panorama/home) and deploy your application!

Refer to the [README.md]({{cookiecutter.project_slug}}/README.md) of the generated project for more information.

## Project template parameter reference

| parameter | default value | description |
|-----------|---------------|-------------|
| project_name | Panorama Video Processor | The human-readable name of the project |
| project_slug | panorama_video_processor | Project slug that can be used in file names, identifiers, etc. Should contain only letters, numbers and underscores. |
| s3_working_bucket | my_bucket | An AWS S3 bucket where the build system have read/write privileges.  |
| s3_working_path | s3://my_bucket/&shy;panorama_projects/&shy;panorama_video_processor | A full S3 URI in the bucket above. This path will be used for model compilation, archiving manifest files and similar. |
| camera_node_name | camera_input | The name of the camera input node in the manifest file. In most of the cases you can leave it to the default value. |
| display_node_name | display_output | The name of the display output node in the manifest file. In most of the cases you can leave it to the default value. |
| code_package_name | panorama_video_processor_logic | The name of the code package. The package name - package version tuple should be unique in your AWS account. |
| code_package_version | 1.0 | The code package version. You can have several versions of your package deployed contemporarily to your account. |
| code_asset_name | panorama_video_processor_logic_asset | The code asset name. |
| code_node_name | panorama_video_processor_logic_node | The name of the code node in the manifest file. |
| model_package_name | panorama_video_processor_model | The name of the model package. The package name - package version tuple should be unique in your AWS account. |
| model_package_version | 1.0 | The model package version. You can have several versions of your package deployed contemporarily to your account. |
| model_asset_name | panorama_video_processor_model_asset | The model asset name. |
| model_node_name | panorama_video_processor_model_node | The name of the model node in the manifest file. |
| model_input_name | input0 | The name of the input of the deep learning model. The model will be compiled with this input name, and you should refer the input with this name from the application source code. |
| model_processing_width | 224 | The width of the input image of the deep learning model. The input frame will be resized to this size before sending it to the model. |
| model_processing_height | 224 | The height of the input image of the deep learning model. The input frame will be resized to this size before sending it to the model. |
