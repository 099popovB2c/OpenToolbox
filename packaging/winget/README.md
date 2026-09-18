# Winget packaging

The files in `0.4.1/` are ready for the Windows Package Manager community repository.

Target community path:

```text
manifests/0/099popovB2c/OpenToolbox/0.4.1/
```

The installer is the standalone x64 portable executable from the v0.4.1 GitHub Release.

## Validate locally

```powershell
winget validate --manifest .\packaging\winget\0.4.1
winget settings --enable LocalManifestFiles
winget install --manifest .\packaging\winget\0.4.1
```

Installer SHA-256:

```text
69954df583002d503a08063adbd259f8c30b3f98a64acb4f90a7e42078f49a31
```

The final publication step is a pull request to `microsoft/winget-pkgs` containing these three YAML files.
