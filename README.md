# cookiecutter-panorama

[Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for [AWS Panorama](https://aws.amazon.com/panorama/) projects.

- GitHub repo: https://github.com/mrtj/cookiecutter-panorama/
- Free software: BSD license

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

Refer to the README.md of the generated project for more information.

