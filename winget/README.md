# WinGet Manifests

WinGet support is handled with YAML manifests. For public installs, submit the
filled manifests to the Microsoft community `winget-pkgs` repository. This
package site can host the actual `.exe`, `.msi`, `.msix`, or bundle installer
files used by those manifests.

This folder is not a complete WinGet source by itself. A private WinGet source
needs the source format supported by the Windows Package Manager client, such as
a REST source.

Use the example manifest set as a template:

```powershell
winget settings --enable LocalManifestFiles
winget install --manifest winget/manifests/TamKungZ.Example/1.0.0/
```
