## PRELIMINARY - OFFICIAL START AT 2026-07-01

<p align="center">
	<img src="img/wtrl_logo_color.svg" alt="Waterloo Logo" width="240">
</p>

## README

_BADGES_

### Install

`package_main` contains the Waterloo Python package and the Sphinx extension.
The package can be installed from a local checkout of this repository:

```bash
cd package_main
pip install .
```

For development, an editable install is often more convenient:

```bash
cd package_main
pip install -e .
```

If you want to build the documentation with the Sphinx extension, install
the optional extra that provides the external `sphinx` dependency:

```bash
cd package_main
pip install ".[sphinx]"
```

The package can also be installed directly from Git:

```bash
pip install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@main#subdirectory=package_main"
```

SSH works as well for authenticated access:

```bash
pip install "git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git@main#subdirectory=package_main"
```

