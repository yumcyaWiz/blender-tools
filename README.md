# Blender-tools

## Setup
- Run `git submodule update --init`
- Copy the directory `ws4py` located at `lib/WebSocket-for-Python/` into `${Blender-root}/2.xx/python/lib/python3.x`
- Add `${blender-tools}/Blender` path to `Scripts` field (`User Preferences` -> `File` tab in Blender) or copy  Blender/ directory to Blender addon directory.
- Reboot Blender and confirm `Blender Tools` appears in add-ons list (`User Preferences` -> `Add-ons` tab). Then activate `Blender Tools`.

## Scene Exporter
Export scene data when the scene is changed.

### Usage
- Add data file path to `Preferences` (add-ons list in Blender). Default value is `/tmp/`
- Click `"Start Scene Exporter"` Button appeared in Tool Shelf.
- Blender export scene data as `"scene.json"` when the scene is changed.

## License
MIT
