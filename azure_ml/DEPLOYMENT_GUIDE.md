# Azure ML deployment — EngageAI

The project is prepared for an Azure Machine Learning managed online endpoint.

## Studio route

1. Open the Azure Machine Learning workspace.
2. Upload/register `model/engageai_model.joblib`.
3. Create a Managed online endpoint named `engageai-endpoint`.
4. Create deployment `blue`.
5. Use `azure_ml/score.py` as scoring script.
6. Use `azure_ml/conda.yaml` as the environment.
7. Use one instance for the prototype.
8. Test with `azure_ml/sample_request.json`.
9. Copy the scoring URI and endpoint key.
10. Configure the application environment:

`AZURE_ML_ENDPOINT=<scoring URI>`
`AZURE_ML_API_KEY=<endpoint key>`

## Azure CLI v2

```bash
az extension add -n ml -y
az login
az account set --subscription "<SUBSCRIPTION_ID>"
az configure --defaults group="<RESOURCE_GROUP>" workspace="<AML_WORKSPACE>"

az ml online-endpoint create -f azure_ml/endpoint.yml
az ml online-deployment create -f azure_ml/deployment.yml --all-traffic
az ml online-endpoint invoke -n engageai-endpoint -r azure_ml/sample_request.json
az ml online-endpoint get-credentials -n engageai-endpoint
```

Delete the endpoint after the demo if it is no longer required:

```bash
az ml online-endpoint delete -n engageai-endpoint --yes
```
