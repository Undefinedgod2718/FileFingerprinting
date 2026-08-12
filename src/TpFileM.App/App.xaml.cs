using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using TpFileM.App.Services;
using Velopack;
using Velopack.Sources;

namespace TpFileM.App;

public partial class App : Application
{
    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        ApplyFontSettings();

        // Check for updates in the background
        _ = CheckForUpdatesAsync();
    }

    internal void ApplyFontSettings()
    {
        var settings = AppSettings.Load();

        if (settings.UseSystemFont)
        {
            Resources["PixelFont"] = new FontFamily("Segoe UI, Microsoft JhengHei");
        }
        else if (!string.IsNullOrWhiteSpace(settings.CustomFontPath) && File.Exists(settings.CustomFontPath))
        {
            try
            {
                var families = Fonts.GetFontFamilies(settings.CustomFontPath);
                var family = System.Linq.Enumerable.FirstOrDefault(families);
                if (family != null)
                {
                    Resources["PixelFont"] = family;
                }
                else
                {
                    FallbackToDefault();
                }
            }
            catch
            {
                FallbackToDefault();
            }
        }
        else
        {
            FallbackToDefault();
        }
    }

    private void FallbackToDefault()
    {
        if (!TryLoadMonocraft())
        {
            Resources["PixelFont"] = new FontFamily("Courier New");
        }
    }

    private bool TryLoadMonocraft()
    {
        try
        {
            _ = new FontFamily("pack://application:,,,/Assets/Fonts/#Monocraft");
            Resources["PixelFont"] = new FontFamily("pack://application:,,,/Assets/Fonts/#Monocraft");
            return true;
        }
        catch
        {
            return false;
        }
    }

    private async Task CheckForUpdatesAsync()
    {
        try
        {
            var mgr = new UpdateManager(new GithubSource("https://github.com/Undefinedgod2718/FileFingerprinting", "", false));

            if (!mgr.IsInstalled) return;

            var newVersion = await mgr.CheckForUpdatesAsync();
            if (newVersion == null) return; // no update available

            // Download new version
            await mgr.DownloadUpdatesAsync(newVersion);

            // Optional: prompt user to restart
            var result = MessageBox.Show(
                $"Version {newVersion.TargetFullRelease.Version} is available and has been downloaded. Restart now to apply?",
                "Update Ready",
                MessageBoxButton.YesNo,
                MessageBoxImage.Information);

            if (result == MessageBoxResult.Yes)
            {
                mgr.ApplyUpdatesAndRestart(newVersion);
            }
        }
        catch (Exception ex)
        {
            // Log or ignore
            Console.WriteLine("Update check failed: " + ex.Message);
        }
    }
}
