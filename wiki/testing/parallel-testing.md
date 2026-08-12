# Parallel testing

```powershell
# 1. Generate fixtures
.\tools\legacy_probe.ps1

# 2. Modern automated check
dotnet test

# 3. Manual legacy
# Launch ..\TPFileM\TPFileM.exe, load each fixture, Generate Key
```

Record mismatches in [test-vectors.md](test-vectors.md).
