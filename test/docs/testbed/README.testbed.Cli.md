
# run tests

```
docker run --network host -v $PWD:/dash --mount src=/etc/localtime,target=/etc/localtime,type=bind,readonly -it dash/keysight bash
cd /dash/test
pytest ./test-cases
```
