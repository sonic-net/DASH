# hardware setup
do the steps in [Prepare Testbed Server](../docs/testbed/README.testbed.software.md) section

# build container
```
git clone https://github.com/Azure/DASH
docker build --no-cache --tag dash/keysight:latest ./DASH/test/environments/keysight
docker tag dash/keysight:latest dash/keysight:1.0.0
```
