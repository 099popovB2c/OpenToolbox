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
f6e43e2876f11b6d9b7ecfa794eb10e5a559935d51e6c6282843c9ad060ba321
```

The final publication step is a pull request to `microsoft/winget-pkgs` containing these three YAML files.
