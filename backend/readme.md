SET THIS TO FALSE !!!
You will most likely get a 401 error saying that you need oauth authentication if this is set to true.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
You will need to run gcloud init and gcloud auth application-default login
