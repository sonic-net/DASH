# Sirius Pipeline

## Build the environment
```
make docker
```

## Build pipeline
```
make clean
make bmv2/dash_pipeline.bmv2/dash_pipeline.json
make sai
make test
```

## Run software switch
```
make run-switch
```

## from a different terminal, run tests (run-switch will run interactive docker view in foreground)
```
make run-test
```
