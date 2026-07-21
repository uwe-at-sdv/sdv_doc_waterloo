### Install from source

`package_main` contains the Waterloo Python package and the Sphinx extension.
The package can be installed from a local checkout of this repository:

```bash
cd package_main
pip install .
```

If you want to build the documentation with the Sphinx extension, install
the optional extra that provides the external `sphinx` dependency:

```bash
cd package_main
pip install ".[sphinx]"
```

The package can also be installed directly from GitHub:

```bash
pip install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@main"
```

SSH works as well for authenticated access:

```bash
pip install "git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git@main"
```
