# Sirius Pipeline
This is a P4 model of the DASH overlay pipeline which uses the [bmv2](https://github.com/p4lang/behavioral-model) from [p4lang](https://github.com/p4lang).

# TODO
* Use modified bmv2 which adds stateful processing. Current versioj is vanilla bmv2.
* Integrate SAI-thrift server from [OCP/SAI](https://github.com/opencomputeproject/SAI)
* Add DASH sevice test cases including SAI-thrift pipeline configuration and traffic tests
* Build Docker image automatically when Dockerfile changes, publish and pull from permanent repo

# CI (Continuous Integration) Via Git Actions
This project contains [Git Actions](https://docs.github.com/en/actions) to perform continuous integration whenever certain actions are performed:
* A Commit or Pull Request of P4 code, Makefiles, scripts, etc.  will trigger a build of bmv2 artifacts and run tests, all in the Azure cloud. Status can be viewed on the Github repo using the "Actions" link in the top of the page. This will be true for forked repos as well as the main Azure/DASH repo.

  Two tests are currently executed in the CI pipeline. These will be increased extensively over time:
  * The `make test` target does a trivial SAI access using a c++ client program. This verifies the libsai-to-P4runtime adaptor over a socket. The test program acts as a P4Runtime client, and the bmv2 simple_switch process is the server.
  * The `make run-ixiac-test` target spins up a two-port traffic-generator engine using the free version of [ixia-c](https://github.com/open-traffic-generator/ixia-c) controlled by a Python [snappi](https://github.com/open-traffic-generator/snappi) client. Using this approach allows scripts to eventually be scaled to line-rate using hardware-bawed traffic generators.

* **Future** - A new Docker image will be built and published to a registry if the Dockerfile changes. Currently, Docker build and publish steps are manual and require permissions to a temporary registry.
* The CI badge will be updated according to the CI build status and appear on the front page of the repo as well as the top-level README page. You can click on this icon to drill down into the Git Actions history and view pass/fail details. Typical icons appear below:

![../assets/CI-badge-passing.svg]     ![../assets/CI-badge-failing.svg] 

# Manually building and running
## Optional - Pull the pre-built Docker image
This is optional, the Docker image will be pulled automatically the first time you run `make p4`. This image contains all the build- and run-time components and packages.

## Optional - expert - build a new Docker image
This step builds a new Docker image on demand, but you shouldn't have to if you use the prebuilt one temporarily available on Docker Hub. A long-term registry (Azure) will be eventually be provisioned. Note, this step can exceed one hour depending upon CPU speed and network bandwidth. 

>**Future** This will be done automatically in the CI pipeline if any changes are made to the Dockerfile.
```
make docker
```

## Build bmv2 pipeline, sai adaptor library and sai test program
```
sudo make clean  # deletes built artifacts
make p4          # compiles p4 code and produces bmv2 runtime .json and P4Info .json
make sai         # autogenerates SAI-to-P4Runtime adaptor, compiles and produces libsai.so
make test        # compiles a simple libsai client program to verify the libsai-p4runtime-bmv2 stack
```

## Run software switch
This will run interactive docker view in foreground. Use additional terminals to perform other tasks.
```
make network      # one-time to make veth's etc.
make run-switch   # launches bmv2 with P4Runtime server
```

## Run simple SAI library test
From a different terminal, run SAI client tests 
```
make run-test     # Performs a single SAI access via a compiled c++ test program
```

## Run ixia-x traffic-generator test
From a different terminal, run SAI client tests 

Install docker-compose used to orchestrate the ixia-c containers:
```
sudo apt install -y docker-compose
```
Run the traffic tests:
```
make run-ixiac-test
```
