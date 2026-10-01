import os
c.LiteBuildConfig.extra_ignore_contents = (r"(^|[/\\])exports([/\\]|$)", r"(^|[/\\])__pycache__([/\\]|$)")
if os.environ.get("JUPYTERLITE_EXTRA_LABEXTENSIONS"):
    c.FederatedExtensionAddon.extra_labextensions_path = [os.environ["JUPYTERLITE_EXTRA_LABEXTENSIONS"]]
