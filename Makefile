# This file is for you! Edit it to implement your own hooks (make targets) into
# the project as automated steps to be executed on locally and in the CD pipeline.

include scripts/init.mk

# ==============================================================================

# Example CI/CD targets are: dependencies, build, publish, deploy, clean, etc.

test: # run tests in a local podman container
	if podman inspect -f '{{.Name}}' playwright > /dev/null; then
		podman rm playwright --force
	fi
		podman build -t bcss-playwright:latest .
		podman run --name playwright bcss-playwright:latest
		podman logs -f playwright
		
dependencies: # Install dependencies needed to build and test the project @Pipeline
	# TODO: Implement installation of your project dependencies

build: # Build the project artefact @Pipeline
	podman build -t bcss-playwright:latest .

publish: # Publish the project artefact @Pipeline
	# TODO: Implement the artefact publishing step

deploy: # Deploy the project artefact to the target environment @Pipeline
	# TODO: Implement the artefact deployment step

clean:: # Clean-up project resources (main) @Operations
	# TODO: Implement project resources clean-up step

config:: # Configure development environment (main) @Configuration
	# TODO: Use only 'make' targets that are specific to this project, e.g. you may not need to install Node.js
	make _install-dependencies

# ==============================================================================

${VERBOSE}.SILENT: \
	build \
	clean \
	config \
	dependencies \
	deploy \
