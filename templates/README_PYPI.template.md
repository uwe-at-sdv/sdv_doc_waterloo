## PRELIMINARY - OFFICIAL START AT 2026-07-01

<p align="center">
	<img src="img/wtrl_logo_color.svg" alt="Waterloo Logo" width="240">
</p>

## README

_BADGES_

### On PyPI

`sdv-doc-waterloo` is the published PyPI package that contains the Waterloo
Python package and the Sphinx extension.

Install it from PyPI:

```bash
pip install sdv-doc-waterloo
```

If you want to build the documentation with the Sphinx extension, install
the optional extra that provides the external `sphinx` dependency:

```bash
pip install "sdv-doc-waterloo[sphinx]"
```

### Development installs

If you prefer a local checkout, install from the repository tree:

```bash
cd package_main
pip install .
```

For active development, an editable install is often more convenient:

```bash
cd package_main
pip install -e .
```

The package can also be installed directly from Git:

```bash
pip install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@main#subdirectory=package_main"
```

SSH works as well for authenticated access:

```bash
pip install "git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git@main#subdirectory=package_main"
```

### Source

The source repository for `sdv-doc-waterloo` is the Waterloo GitHub
repository:

- `https://github.com/uwe-at-sdv/sdv_doc_waterloo`
