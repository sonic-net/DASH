# hardware setup
https://github.com/Azure/DASH/blob/master/docs/testbed/README.testbed.Setup.md
  - do the steps in "Prepare Testbed Server" section

# build container
```
git clone https://github.com/Azure/DASH
docker build --no-cache --tag dash/keysight:latest ./DASH/test/environments/keysight
docker tag dash/keysight:latest dash/keysight:1.0.0
```

# run tests
copy sdfasfasdfasfasdfsadfasdfasfasdf TODOTODOdsfsdfsf./testbeds/
```
docker run --network host -v $PWD:/data --mount src=/etc/localtime,target=/etc/localtime,type=bind,readonly -it dash/keysight bash
cd /data/DASH/test
pytest --testbed-file ./testbeds/testbed_file.yaml --logs-path ./logs --log-level debug --test-suite ./tests
```
