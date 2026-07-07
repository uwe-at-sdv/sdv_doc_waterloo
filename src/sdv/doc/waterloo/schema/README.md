# Notes

JSON Schemas hosted at sci-d-vis.com are managed by uwe-at-sdv or
alternatively someone else at Science-D-Vsions GmbH.

The upload is done by tools/sdv_wtrl_upload_json_schema.sh in
the root directory parent to the github-branches (i.e. it is not
part of the distribution).

Any JSON Schema relevant for the Waterloo project must be documented
in the section marked by the reST-label *json_io_layer_validation*,
in version-agnostic way (using placeholders like *.*.*).

Any JSON Schema relevant for the Waterloo project must be taken into
account in `waterlint version-json`.
